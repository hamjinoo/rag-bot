# RAG 파이프라인 구현 가이드

## 개요
이 문서는 문서 업로드부터 답변 생성까지의 **엔드 투 엔드 RAG 파이프라인**을 구축하기 위한 상세 절차를 제공합니다. FastAPI 백엔드와 Chroma 로컬 벡터스토어를 기준으로 설명하며, 추후 다른 DB나 임베딩 모델로 확장할 수 있도록 대안도 함께 제시합니다.

## 시스템 구성요소
- `FastAPI` 앱 (`app/main.py`)
- 파이프라인 모듈 (`app/pipelines.py`): 업로드 → 임베딩 → 색인
- 검색 모듈 (`app/retriever.py`): Top-k + MMR + 임계치
- LLM 모듈 (`app/llm.py`): OpenAI GPT 기반 답변 생성
- 로그/권한 모듈 (`app/logging.py`, `app/auth.py`) — Week 6에 확장
- `data/` 디렉터리: 원본 문서 보관
- `vector_store/` 혹은 `chroma/` (환경변수 `VECTOR_DB_PATH`)

## 선행 준비
1. Python 3.10 이상 가상환경 생성 및 패키지 설치
   - 상세한 설치 방법은 [`appendix/setup-requirements.md`](../appendix/setup-requirements.md)를 참고하세요.
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```
2. `.env` 파일 생성
   ```
   OPENAI_API_KEY=sk-...
   VECTOR_DB_PATH=./chroma
   CHUNK_SIZE=600
   CHUNK_OVERLAP=120
   ```
3. FastAPI 서버 실행
   ```bash
   uvicorn app.main:app --reload
   ```

> **Windows 팁**: `setx OPENAI_API_KEY "값"` 과 같이 시스템 환경변수로 등록하면 IDE에서도 인식됩니다. 프로젝트 루트에서 명령을 실행하세요.

## 파이프라인 단계

### 1. 문서 업로드 및 파싱
- `/upload` 엔드포인트에서 `PDF, Docx, CSV` 파일 지원
- 텍스트 추출 라이브러리:
  - PDF: `pypdf` 또는 `pdfminer.six`
  - Docx: `python-docx`
  - CSV: `pandas`
- 파일 메타데이터(`doc_id`, `title`, `source_path`, `page_number`)를 DB 또는 JSON으로 저장
- **Tip**: 업로드 시 파일명을 기준으로 중복 여부 체크 → 기존 벡터 삭제 후 재색인
- **실행 순서**
  1. `app/schemas.py`에 업로드 요청/응답 모델 정의 (Pydantic `BaseModel`)
  2. `app/main.py`에서 `UploadFile`을 받아 임시 폴더에 저장 (`data/uploads/{uuid}` 구조)
  3. 파일 타입에 따라 파서 함수를 호출하도록 `pipelines.py`에 `parse_document(path)` 함수 작성
  4. 파싱 결과와 메타데이터를 `Document` 객체(예: LangChain) 또는 커스텀 dict로 반환

### 2. 청크 분할
- 기본값: `chunk_size=600`, `chunk_overlap=120`
- 긴 문서일수록 overlap을 늘려 문맥 보존
- 코드 예시:

```startLine:endLine:app/pipelines.py
# ... existing code ...
def split_documents(text: str, metadata: dict) -> list[Document]:
    return text_splitter.create_documents(
        [text],
        metadatas=[metadata]
    )
# ... existing code ...
```

- **대안**: 한국어 문서 비중이 높다면 `Kiwi`, `KoNLPy` 기반 어절 단위 분리도 고려

### 3. 임베딩 생성
- 초기: OpenAI `text-embedding-3-small` (비용 저렴, 속도 빠름)
- 환경변수 `EMBED_MODEL`로 모델 지정
- 토큰 비용 계산을 위해 `len(text.split())` 또는 `tiktoken`으로 길이 산출
- **향후 업그레이드**: 로컬 환경 시 `BGE-m3`, `E5-mistral` 사용 (Week 6 이후)
- **구현 팁**
  - `app/llm.py`에 `EmbeddingClient` 클래스를 만들어, OpenAI/로컬 모델을 전략 패턴으로 교체 가능하게 설계
  - 임베딩 호출 전 텍스트 길이가 8,000자 이상이면 요약 후 재시도 로직 추가
  - 비용 계산: `token_count / 1000 * 단가` 를 `Decimal` 타입으로 저장하여 반올림 이슈 방지

### 4. 벡터 색인
- Chroma 초기화 예시:

```startLine:endLine:app/pipelines.py
# ... existing code ...
chroma = Chroma(
    collection_name="rag_documents",
    embedding_function=embedding_fn,
    persist_directory=settings.vector_db_path,
)
# ... existing code ...
```

- 문서 삽입 시 `metadata`에 `doc_id`, `page`, `source_url`, `access_level` 저장
- 색인 이후 `chroma.persist()` 호출로 디스크에 저장
- **Tip**: 재색인 전 `delete(where={"doc_id": doc_id})` 로 정리
- **테스트 방법**
  - `python -m scripts.debug_chroma --doc_id sample-doc` 스크립트를 만들어 현재 색인 상태를 조회
  - `persist_directory` 경로를 삭제하기 전에 반드시 백업(zip) 후 진행

### 5. 검색 & 재랭킹
- 기본 검색 파라미터
  - `top_k = 5`
  - `mmr = True`
  - `fetch_k = 20` (MMR용 확장 후보 수)
  - `score_threshold = 0.75`
- `retriever.py`에서 `similarity_search_with_relevance_scores` 활용
- `score < threshold`인 경우 “근거를 찾지 못했습니다” 메시지 반환
- 동일한 질문 반복 시 캐시(예: `functools.lru_cache` or Redis) 적용 고려

### 6. LLM 응답 생성
- 프롬프트 구성 요소
  - 사용자 질문
  - 선택된 컨텍스트(문서·페이지·요약)
  - 지시문: “출처 없는 내용 금지, 출처는 bullet list로 기재”
- 출력 포맷 예시
  ```
  답변 본문

  출처:
  - [문서명 | 페이지 | URL]
  ```
- 답변 길이 제한: 350~500자 권장, 길어질 경우 “더보기” 가이드 포함
- **프롬프트 샘플**
  ```
  시스템: 너는 사내 문서 기반 질문에 답하는 전문가야. 아래 규칙을 지켜.
  1) 제공된 컨텍스트에서만 답변.
  2) 출처는 반드시 목록으로 기재.
  3) 근거가 없으면 답변 대신 문서 업로드를 요청.
  
  사용자 질문: {question}
  컨텍스트:
  {context}
  ```
- **테스트**
  - `scripts/test_answer.py --question "자기계발비 신청 방법?"` 으로 단일 질문 테스트
  - 응답 JSON에 `sources` 배열이 비어 있으면 실패로 간주하고 프롬프트 수정

### 7. 응답 로깅
- Week 1에는 JSON 로그(`logs/responses.jsonl`) 저장부터 시작
- 필드: `timestamp`, `channel`, `question`, `answer`, `sources`, `token_in`, `token_out`, `cost`
- Week 6에 DB로 마이그레이션
- **샘플 로그 구조**
  ```json
  {
    "timestamp": "2025-11-10T21:15:04+09:00",
    "channel": "web",
    "question": "복지포인트 사용 기한?",
    "answer": "복지포인트는 매년 12월 31일까지...",
    "sources": [
      {"title": "복지 포털 가이드", "page": "p.3", "url": "https://intra/..."}
    ],
    "token_in": 812,
    "token_out": 180,
    "cost": 0.0023
  }
  ```

## 테스트 & 품질관리
- `tests/pipeline_smoke_test.py` 등 간단 스모크 테스트 추가 권장
- 평가 스크립트
  ```bash
  python scripts/evaluate.py --dataset data/eval.csv
  ```
- 지표
  - `정확도`: 기대 정답과 일치 여부
  - `근거 일치율`: 실제 참조한 문서와 기대 출처 비교
  - `무응답률`: 임계치 이하 시 응답 회피 비율
- **CI 설정 예시**
  - GitHub Actions에서 `pytest tests/ -m "pipeline"` 워크플로우 생성
  - `VECTOR_DB_PATH=./tmp/chroma` 와 같이 테스트용 디렉터리를 사용하도록 환경변수 분리

## 운영 팁
- 새 문서 업로드 후에는 항상 재색인 + 스모크 테스트 수행
- 장기적으로는 문서 버전 관리(버전/리비전 필드)를 추가해 롤백 대비
- 벡터 DB 백업은 일주일 1회 이상 (Chroma 폴더 ZIP)
- AWS S3나 Google Drive에 주간 백업 자동 업로드 스크립트(`python scripts/backup.py`)를 추가하면 복구가 쉬워집니다.

## 다음 단계
- 텔레그램/카카오 챗봇 연동은 [`implementation/bots.md`](bots.md)를 참고하세요.
- 정확도 개선 및 평가 체계는 Week 4 로드맵과 연계해 진행합니다.

