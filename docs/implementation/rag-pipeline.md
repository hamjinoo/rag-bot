# RAG 파이프라인 구현 가이드

> **목표**: “업로드 → 임베딩 → 검색 → 답변” 플로우를 FastAPI + LangChain + Chroma로 처음부터 끝까지 구축한다.

---

## 🎯 학습 목표

| Step | 결과                               | 핵심 역량                                 |
| ---- | ---------------------------------- | ----------------------------------------- |
| 1    | 업로드된 문서를 표준 포맷으로 파싱 | 파일 파서 구성, 메타데이터 관리           |
| 2    | 텍스트를 청크로 분리하고 임베딩    | LangChain TextSplitter & OpenAI Embedding |
| 3    | 벡터 DB에 영구 저장                | Chroma 컬렉션 관리, 재색인 전략           |
| 4    | 유사도 검색 + GPT 응답 생성        | `score_threshold`, 프롬프트 가드레일      |
| 5    | 요청/응답/비용 로깅                | 비용 계산, JSON/DB 로깅, 품질 지표        |

---

## 🛠️ 사전 준비

| 항목        | 내용                                                                                                            |
| ----------- | --------------------------------------------------------------------------------------------------------------- |
| 환경        | Python 3.10+, Git, VS Code/PyCharm                                                                              |
| 패키지      | `pip install -r requirements.txt` (참고: [`appendix/setup-requirements.md`](../appendix/setup-requirements.md)) |
| 환경변수    | `.env`에 `OPENAI_API_KEY`, `VECTOR_DB_PATH`, `CHUNK_SIZE`, `CHUNK_OVERLAP`                                      |
| 샘플 데이터 | `data/`에 PDF/Docx/CSV 각 1개 이상                                                                              |

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

---

## 💻 샘플 코드 시작점

```python
# app/pipelines.py
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.vector_store import vector_client
from app.parsers import parse_document


async def process_upload(file) -> str:
    text, metadata = parse_document(file)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=120,
    )
    chunks = splitter.create_documents([text], metadatas=[metadata])
    vector_client.add_documents(chunks)
    return metadata["doc_id"]
```

```python
# app/retriever.py
from app.vector_store import vector_client
from app.llm import build_prompt_and_ask

async def retrieve_answer(question: str) -> dict:
    docs = vector_client.similarity_search(question, k=5, score_threshold=0.75)
    if not docs:
        return {
            "answer": "자료에서 근거를 찾지 못했습니다. 관련 문서를 업로드해 주세요.",
            "sources": [],
        }
    return await build_prompt_and_ask(question, docs)
```

---

## 🔄 단계별 실습 가이드

### 1. 문서 업로드 & 파싱

```python
# app/parsers/pdf.py
from pypdf import PdfReader

def parse_pdf(file) -> tuple[str, dict]:
    reader = PdfReader(file)
    text = "\n\n".join(page.extract_text() for page in reader.pages)
    metadata = {
        "doc_id": file.filename,
        "title": file.filename,
        "source_path": f"data/uploads/{file.filename}",
        "page_count": len(reader.pages),
    }
    return text, metadata
```

- 파일 확장자에 따라 파서 라우팅 (`app/parsers/__init__.py`)
- 업로드 시 `data/uploads/{uuid}` 경로에 저장 후 파서 호출
- 메타데이터에 `access_level`, `team` 필드를 추가해 Week 6 권한 기능과 연계

### 2. 청크 분할

| 설정            | 기본값                    | 조정 가이드                                        |
| --------------- | ------------------------- | -------------------------------------------------- |
| `chunk_size`    | 600                       | 문서가 길수록 증가, GPT 4o mini 기준 800 이하 추천 |
| `chunk_overlap` | 120                       | 정보 손실이 있으면 150까지 확장                    |
| `separators`    | `["\n\n", "\n", " ", ""]` | 제목, 문단 단위 분리에 활용                        |

```python
splitter = RecursiveCharacterTextSplitter(
    chunk_size=settings.CHUNK_SIZE,
    chunk_overlap=settings.CHUNK_OVERLAP,
    separators=["\n\n", "\n", " ", ""],
)
```

### 3. 임베딩 생성

```python
# app/embeddings.py
from langchain_openai import OpenAIEmbeddings

embedding = OpenAIEmbeddings(model="text-embedding-3-small")

def embed_texts(chunks):
    vectors = embedding.embed_documents([c.page_content for c in chunks])
    return vectors
```

- 토큰 길이를 `tiktoken`으로 측정해 비용 추정
- 향후 비용 절감을 위해 `sentence-transformers` 기반 로컬 모델로 교체 가능

### 4. 벡터 색인

```python
# app/vector_store.py
from langchain.vectorstores import Chroma
from app.embeddings import embedding
from app.config import settings

vector_client = Chroma(
    collection_name="rag_documents",
    embedding_function=embedding,
    persist_directory=settings.vector_db_path,
)
```

- 재색인 시 `vector_client.delete(where={"doc_id": doc_id})`로 기존 데이터 정리
- `persist()` 호출 후 `vector_db_path` 폴더가 생성되었는지 확인

### 5. 검색 & 응답 생성

```python
# app/llm.py
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)

async def build_prompt_and_ask(question: str, docs):
    context = "\n\n".join(
        f"[{doc.metadata.get('title','문서')} | p.{doc.metadata.get('page','?')}] {doc.page_content}"
        for doc in docs
    )
    messages = [
        SystemMessage(content=(
            "당신은 문서 기반 Q&A 어시스턴트입니다.\n"
            "제공된 컨텍스트 안에서만 답변하고, 마지막에 출처 목록을 bullet로 나열하세요.\n"
            "근거가 없으면 답변 대신 문서 업로드를 요청하세요."
        )),
        HumanMessage(content=f"질문: {question}\n\n컨텍스트:\n{context}"),
    ]
    completion = await llm.apredict_messages(messages)
    return {
        "answer": completion.content,
        "sources": [
            {
                "title": doc.metadata.get("title"),
                "page": doc.metadata.get("page"),
                "url": doc.metadata.get("source_url"),
            }
            for doc in docs
        ],
    }
```

### 6. 응답 로깅 & 비용 계산

```python
# app/logging.py
from datetime import datetime
from decimal import Decimal

PROMPT_PRICE = Decimal("0.0005")  # per 1K tokens
COMPLETION_PRICE = Decimal("0.0015")

def calc_cost(token_in: int, token_out: int) -> Decimal:
    return (Decimal(token_in) / 1000 * PROMPT_PRICE) + (
        Decimal(token_out) / 1000 * COMPLETION_PRICE
    )

def log_response(payload: dict):
    payload["created_at"] = datetime.utcnow().isoformat()
    with open("logs/responses.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")
```

Week 6 이후에는 SQLAlchemy 모델로 마이그레이션해 `/admin` 대시보드에서 시각화합니다.

---

## ✅ 체크리스트

- [ ] 파일 업로드 후 `vector_client.count()`가 0보다 크다.
- [ ] `/ask` 응답에 `sources` 배열이 포함된다.
- [ ] `score_threshold` 이하일 때 “근거 없음” 메시지가 출력된다.
- [ ] `logs/responses.jsonl`에 `token_in/out`, `cost`가 기록된다.
- [ ] `scripts/evaluate.py`로 정답률/근거 일치율을 측정했다.

---

## 🧪 테스트 & 품질 관리

| 테스트        | 목적                         | 명령                                                 |
| ------------- | ---------------------------- | ---------------------------------------------------- |
| 스모크 테스트 | 업로드 → 질문 흐름 정상 동작 | `pytest tests/test_pipeline.py -m smoke`             |
| 평가 스크립트 | 정확도·근거 일치율 확인      | `python scripts/evaluate.py --dataset data/eval.csv` |
| 부하 테스트   | 다중 요청 대응               | `locust -f scripts/locustfile.py` (선택)             |

CI 예시:
```yaml
- name: Pipeline Tests
  run: |
    pip install -r requirements.txt
    VECTOR_DB_PATH=./tmp/chroma pytest tests/ -m "pipeline"
```

---

## 🔁 운영 팁

- 새 문서 업로드 후에는 반드시 재색인 & 스모크 테스트 수행
- Chroma 폴더는 주 1회 이상 백업 (ZIP → S3/Google Drive)
- 문서 버전 관리(Revision 필드)를 추가해 롤백을 대비
- 자주 질문되는 문서는 `sources` 필드에 링크를 추가해 사용자가 바로 열람 가능하게 한다.

---

## 📚 참고 & 다음 학습

- [LangChain 텍스트 분할 공식 문서](https://python.langchain.com/docs/modules/data_connection/document_transformers/)
- [Chroma 문서](https://docs.trychroma.com/)
- [OpenAI 가격표](https://openai.com/pricing)
- 권한/로그 확장은 [`implementation/web-admin.md`](web-admin.md)를 참고
- 채널 연동은 [`implementation/bots.md`](bots.md)에서 이어서 진행

문제가 발생하면 [`appendix/troubleshooting.md`](../appendix/troubleshooting.md)를 먼저 확인하세요.

