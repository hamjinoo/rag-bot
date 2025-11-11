# Step 1: RAG 파이프라인 구현 - 나만의 AI 검색엔진 만들기

> **목표**: "업로드 → 임베딩 → 검색 → 답변" 플로우를 FastAPI + LangChain + Chroma로 처음부터 끝까지 구축한다.

---

## 🎯 이 단계를 배우는 이유

### 왜 RAG(Retrieval-Augmented Generation)인가?

**RAG는 "나만의 ChatGPT"를 만드는 기술**입니다.

일반 ChatGPT의 한계:
- ❌ 회사 내부 문서는 모릅니다 (학습 안 됨)
- ❌ 최신 정보가 없습니다 (학습 시점 이후 데이터 부재)
- ❌ 출처를 제시하지 못합니다 (할루시네이션 위험)

RAG 챗봇의 강점:
- ✅ 우리 회사 문서로 답변 (PDF, Docx, CSV 업로드)
- ✅ 항상 최신 정보 (문서만 업데이트하면 됨)
- ✅ 출처 명시 (페이지 번호, URL 제공)

### 프리랜서 입장에서 왜 필요한가?

1. **중소기업의 실제 니즈**
   - "사내 규정집이 200페이지인데 직원들이 안 읽어요"
   - "고객 문의가 반복되는데 일일이 답변하기 힘들어요"
   - "신입사원 교육 자료를 챗봇으로 만들 수 있나요?"

2. **외주 단가가 높습니다**
   - 단순 홈페이지: 200~500만원
   - **RAG 챗봇: 800~2,000만원** (AI 기술력 프리미엄)
   - 월 유지보수: 50~200만원

3. **경쟁자가 적습니다**
   - 대부분은 "OpenAI API 붙이기"만 합니다
   - 문서 관리, 권한, 비용 최적화까지 하는 사람은 드뭅니다

### 이 문서를 끝내면 이렇게 됩니다

**Before (일반 개발자)**
```
고객: "우리 회사 규정집 챗봇 만들어주세요."
개발자: "ChatGPT API 연결해드릴게요."
고객: "그럼 어떻게 우리 문서를 학습시키나요?"
개발자: "...?" 💥
```

**After (이 문서 학습 후)**
```
고객: "우리 회사 규정집 챗봇 만들어주세요."
여러분: "PDF 업로드하시면 자동으로 색인됩니다.
       출처도 표시되고, 권한별로 접근 제어도 가능합니다.
       데모 보여드릴까요?" ✨
```

---

## 💡 핵심 개념 먼저 이해하기

### 1. RAG가 뭐야?

**전통적인 ChatGPT**
```
질문 → GPT → 답변 (학습된 지식만 사용)
```

**RAG 방식**
```
질문 → 관련 문서 검색 → 검색 결과 + 질문 → GPT → 답변
```

**비유로 이해하기:**
- 일반 ChatGPT = 모든 걸 외우고 시험 보는 학생
- RAG = 자료 검색해서 답변하는 학생 (오픈북 시험)

### 2. 임베딩(Embedding)이란?

**문제 상황:**
```python
# 이렇게 검색하면 작동 안 함
if "복지포인트" in 문서:
    return 문서
# "복리후생 포인트"라고 쓰여 있으면? 못 찾음 💥
```

**임베딩의 해결책:**
```python
# 의미를 숫자 벡터로 변환
"복지포인트 신청" → [0.2, 0.8, 0.1, ...] (1536차원)
"복리후생 포인트" → [0.19, 0.81, 0.11, ...] (유사한 벡터)

# 코사인 유사도 → 95% 일치! ✅
```

**왜 이게 중요한가?**
- 동의어, 유사 표현 자동 처리
- "연차 신청"과 "휴가 내는 법"을 같은 의미로 인식

### 3. 벡터 DB가 필요한 이유

일반 DB (MySQL, PostgreSQL):
```sql
SELECT * FROM docs WHERE title = '규정집';  -- 정확히 일치해야 함
```

벡터 DB (Chroma, Pinecone):
```python
vector_db.similarity_search("연차 사용 방법")
# → "휴가 관리 규정" 문서를 유사도 0.89로 찾아냄 ✨
```

### 4. 청크(Chunk)는 왜 나누나?

**문제:**
- GPT 입력 토큰 제한: 4,096 ~ 128,000 토큰
- 규정집 전체(300페이지)를 한 번에 넣으면 비용 폭탄 💸

**해결:**
```
규정집 300페이지
→ 600자씩 잘라서 500개 청크로 분리
→ 질문과 관련된 5개 청크만 GPT에 전달
→ 비용 1/100 절감! 🎉
```

**Chunk Overlap은 왜?**
```
청크1: "연차는 입사 1년 후부터 15일이 부여되며"
청크2: "부여되며, 사용은 근태 시스템에서 신청합니다"
        ↑ 120자 겹침 (문맥 보존)
```

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

## 🔄 따라하기 - 처음부터 끝까지

### Step 1: 프로젝트 폴더 구조 만들기

**명령어 (Windows CMD)**
```bash
cd C:\Users\%USERNAME%\Desktop
mkdir rag-bot
cd rag-bot
mkdir app app\parsers data data\uploads logs tests scripts web
```

**명령어 (Mac/Linux)**
```bash
cd ~/Desktop
mkdir -p rag-bot/{app/parsers,data/uploads,logs,tests,scripts,web}
cd rag-bot
```

**결과 확인:**
```
rag-bot/
├── app/          ← FastAPI 백엔드
├── data/         ← 업로드된 문서
├── logs/         ← 응답 로그
├── web/          ← 웹 데모 UI
└── tests/        ← 테스트 코드
```

---

### Step 2: 가상환경 & 패키지 설치

#### 2-1. 가상환경 생성

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**성공 확인:**
```bash
# 프롬프트 앞에 (.venv) 표시되면 성공
(.venv) C:\Users\...\rag-bot>
```

#### 2-2. requirements.txt 작성

**파일 생성:** `requirements.txt`

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
langchain==0.1.0
langchain-openai==0.0.2
chromadb==0.4.18
pypdf==3.17.1
python-docx==1.1.0
pandas==2.1.3
python-multipart==0.0.6
python-dotenv==1.0.0
tiktoken==0.5.2
```

**설치:**
```bash
pip install -r requirements.txt
```

**5분 정도 걸립니다. 커피 한 잔 ☕**

---

### Step 3: 환경변수 설정

**파일 생성:** `.env`

```env
OPENAI_API_KEY=sk-proj-여기에_본인의_키_입력
VECTOR_DB_PATH=./chroma
CHUNK_SIZE=600
CHUNK_OVERLAP=120
```

**OpenAI API 키 발급 방법:**
1. https://platform.openai.com/api-keys 접속
2. "Create new secret key" 클릭
3. 키 복사 → `.env` 파일에 붙여넣기
4. ⚠️ **절대 GitHub에 올리지 마세요!** (`.gitignore`에 `.env` 추가 필수)

---

### Step 4: 문서 파서 작성

#### 4-1. PDF 파서

**파일 생성:** `app/parsers/pdf.py`

```python
from pypdf import PdfReader
from typing import Tuple, Dict

def parse_pdf(file_path: str) -> Tuple[str, Dict]:
    """
    PDF 파일을 읽어서 텍스트와 메타데이터 반환
    
    Args:
        file_path: PDF 파일 경로
        
    Returns:
        (전체 텍스트, 메타데이터 딕셔너리)
    """
    reader = PdfReader(file_path)
    
    # 모든 페이지를 \n\n으로 구분해서 합침
    text = "\n\n".join(
        page.extract_text() 
        for page in reader.pages
    )
    
    metadata = {
        "doc_id": file_path.split("/")[-1],  # 파일명만 추출
        "title": file_path.split("/")[-1],
        "source_path": file_path,
        "page_count": len(reader.pages),
    }
    
    return text, metadata
```

**왜 이렇게 하나요?**
- `\n\n`: 페이지 구분을 명확히 해서 청크 분할 시 페이지 경계 보존
- `metadata`: 나중에 출처 표시할 때 사용 ("규정집.pdf 3페이지 참고")

#### 4-2. 파일 타입 라우터

**파일 생성:** `app/parsers/__init__.py`

```python
from pathlib import Path
from .pdf import parse_pdf

def parse_document(file_path: str):
    """
    파일 확장자에 따라 적절한 파서 선택
    """
    ext = Path(file_path).suffix.lower()
    
    if ext == ".pdf":
        return parse_pdf(file_path)
    elif ext == ".docx":
        from .docx_parser import parse_docx
        return parse_docx(file_path)
    elif ext == ".csv":
        from .csv_parser import parse_csv
        return parse_csv(file_path)
    else:
        raise ValueError(f"지원하지 않는 파일 형식: {ext}")
```

**테스트 방법:**

**파일 생성:** `tests/test_parser.py`

```python
from app.parsers import parse_document

def test_pdf_parser():
    # 테스트용 PDF 준비 (구글에서 "샘플 PDF" 다운로드)
    text, metadata = parse_document("data/sample.pdf")
    
    assert len(text) > 0, "텍스트가 비어있습니다"
    assert metadata["page_count"] > 0, "페이지 수가 0입니다"
    print(f"✅ 파싱 성공: {len(text)}자, {metadata['page_count']}페이지")

if __name__ == "__main__":
    test_pdf_parser()
```

**실행:**
```bash
python tests/test_parser.py
```

**결과 예시:**
```
✅ 파싱 성공: 15243자, 12페이지
```

---

### Step 5: 청크 분할 & 임베딩

**파일 생성:** `app/pipelines.py`

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()

# 환경변수에서 설정 읽기
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "600"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "120"))

def split_text(text: str, metadata: dict) -> List[Document]:
    """
    긴 텍스트를 청크로 분할
    
    Args:
        text: 전체 텍스트
        metadata: 문서 메타데이터
        
    Returns:
        Document 객체 리스트 (각 청크)
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", " ", ""],  # 문단 → 줄 → 단어 → 문자 순
    )
    
    chunks = splitter.create_documents(
        texts=[text],
        metadatas=[metadata]
    )
    
    print(f"✅ 청크 분할 완료: {len(chunks)}개")
    return chunks
```

**테스트:**

**파일 생성:** `tests/test_chunking.py`

```python
from app.parsers import parse_document
from app.pipelines import split_text

def test_chunking():
    # 1. PDF 파싱
    text, metadata = parse_document("data/sample.pdf")
    print(f"📄 원본 텍스트: {len(text)}자")
    
    # 2. 청크 분할
    chunks = split_text(text, metadata)
    print(f"🔪 청크 개수: {len(chunks)}개")
    
    # 3. 첫 청크 확인
    print(f"\n📌 첫 번째 청크 (600자):")
    print(chunks[0].page_content[:200] + "...")
    
    # 4. 오버랩 확인
    if len(chunks) >= 2:
        chunk1_end = chunks[0].page_content[-50:]
        chunk2_start = chunks[1].page_content[:50:]
        print(f"\n🔗 청크1 끝: ...{chunk1_end}")
        print(f"🔗 청크2 시작: {chunk2_start}...")

if __name__ == "__main__":
    test_chunking()
```

**실행:**
```bash
python tests/test_chunking.py
```

**결과 예시:**
```
📄 원본 텍스트: 15243자
✅ 청크 분할 완료: 28개
🔪 청크 개수: 28개

📌 첫 번째 청크 (600자):
제1장 총칙
제1조 (목적) 이 규정은 회사의 인사 관리에 관한 기본 사항을 정함으로써...

🔗 청크1 끝: ...연차 휴가는 입사 1년 후부터 15일이 부여되며
🔗 청크2 시작: 부여되며, 사용은 근태 관리 시스템에서 신청합니다...
```

**👀 확인 포인트:**
- 청크 개수가 적절한가? (너무 많으면 검색 느려짐, 너무 적으면 정확도 떨어짐)
- 오버랩이 제대로 되는가? (청크1 끝과 청크2 시작이 겹쳐야 함)

---

### Step 6: 벡터 DB 색인 (Chroma)

**파일 생성:** `app/vector_store.py`

```python
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.schema import Document
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()

# 임베딩 모델 초기화
embedding = OpenAIEmbeddings(
    model="text-embedding-3-small",  # 비용 절감형
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

# Chroma 벡터 DB 클라이언트
vector_client = Chroma(
    collection_name="rag_documents",
    embedding_function=embedding,
    persist_directory=os.getenv("VECTOR_DB_PATH", "./chroma"),
)

def add_documents(chunks: List[Document]):
    """
    청크를 벡터 DB에 저장
    """
    vector_client.add_documents(chunks)
    vector_client.persist()  # 디스크에 저장
    print(f"✅ {len(chunks)}개 청크를 벡터 DB에 저장했습니다.")

def search_documents(query: str, k: int = 5):
    """
    질문과 유사한 문서 검색
    """
    results = vector_client.similarity_search_with_relevance_scores(
        query=query,
        k=k,
        score_threshold=0.75  # 유사도 75% 이상만
    )
    return results
```

**전체 파이프라인 테스트:**

**파일 생성:** `tests/test_full_pipeline.py`

```python
from app.parsers import parse_document
from app.pipelines import split_text
from app.vector_store import add_documents, search_documents

def test_full_pipeline():
    print("📂 Step 1: PDF 파싱")
    text, metadata = parse_document("data/sample.pdf")
    print(f"   ✅ {len(text)}자 추출\n")
    
    print("🔪 Step 2: 청크 분할")
    chunks = split_text(text, metadata)
    print(f"   ✅ {len(chunks)}개 청크 생성\n")
    
    print("🗄️ Step 3: 벡터 DB 색인 (임베딩 생성 중... 30초 소요)")
    add_documents(chunks)
    print(f"   ✅ 색인 완료\n")
    
    print("🔍 Step 4: 검색 테스트")
    query = "연차 휴가는 몇 일인가요?"
    results = search_documents(query, k=3)
    
    if results:
        print(f"   ✅ {len(results)}개 문서 발견:")
        for doc, score in results:
            print(f"      📄 유사도 {score:.2f}: {doc.page_content[:100]}...")
    else:
        print("   ❌ 관련 문서를 찾지 못했습니다.")

if __name__ == "__main__":
    test_full_pipeline()
```

**실행:**
```bash
python tests/test_full_pipeline.py
```

**결과 예시:**
```
📂 Step 1: PDF 파싱
   ✅ 15243자 추출

🔪 Step 2: 청크 분할
   ✅ 28개 청크 생성

🗄️ Step 3: 벡터 DB 색인 (임베딩 생성 중... 30초 소요)
✅ 28개 청크를 벡터 DB에 저장했습니다.
   ✅ 색인 완료

🔍 Step 4: 검색 테스트
   ✅ 3개 문서 발견:
      📄 유사도 0.89: 제3조 (연차 휴가) 입사 1년 후부터 15일의 연차가 부여되며...
      📄 유사도 0.82: 휴가 사용은 근태 관리 시스템에서 최소 3일 전 신청...
      📄 유사도 0.76: 미사용 연차는 익년 상반기까지 이월 가능...
```

**🎉 여기까지 성공했다면:**
- ✅ 문서 업로드 → 임베딩 → 검색 파이프라인 완성!
- ✅ `chroma/` 폴더에 벡터 DB 파일 생성됨
- ✅ 의미 기반 검색이 작동함 (키워드 정확히 일치 안 해도 찾아냄)

---

### Step 7: GPT 응답 생성

**파일 생성:** `app/llm.py`

```python
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from typing import List, Tuple, Any
import os
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.2,  # 낮을수록 일관적 (0~1)
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

async def generate_answer(question: str, search_results: List[Tuple[Any, float]]) -> dict:
    """
    검색 결과를 바탕으로 GPT 답변 생성
    
    Args:
        question: 사용자 질문
        search_results: [(Document, score), ...]
        
    Returns:
        {"answer": "...", "sources": [...]}
    """
    if not search_results:
        return {
            "answer": "❌ 관련 문서를 찾지 못했습니다. 문서를 업로드하거나 질문을 구체화해 주세요.",
            "sources": []
        }
    
    # 컨텍스트 구성
    context = "\n\n".join([
        f"[문서 {i+1}] {doc.page_content}"
        for i, (doc, score) in enumerate(search_results)
    ])
    
    # 프롬프트 구성
    system_prompt = """당신은 문서 기반 Q&A 어시스턴트입니다.

규칙:
1. 제공된 컨텍스트 안에서만 답변하세요.
2. 근거가 없으면 "문서에서 찾을 수 없습니다"라고 명시하세요.
3. 답변 끝에 출처를 bullet 리스트로 나열하세요.

출력 형식:
답변 내용...

**출처:**
- [문서명] 참고
"""
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"질문: {question}\n\n컨텍스트:\n{context}")
    ]
    
    # GPT 호출
    response = await llm.apredict_messages(messages)
    
    # 출처 정리
    sources = [
        {
            "title": doc.metadata.get("title", "문서"),
            "page": doc.metadata.get("page_count", "?"),
            "score": round(score, 2)
        }
        for doc, score in search_results
    ]
    
    return {
        "answer": response.content,
        "sources": sources
    }
```

**테스트:**

**파일 생성:** `tests/test_answer.py`

```python
import asyncio
from app.vector_store import search_documents
from app.llm import generate_answer

async def test_answer():
    query = "연차 휴가 신청 방법은?"
    
    print(f"🔍 검색 중: {query}")
    results = search_documents(query, k=3)
    
    print(f"🤖 GPT 답변 생성 중...")
    answer_data = await generate_answer(query, results)
    
    print("\n" + "="*60)
    print(f"질문: {query}")
    print("="*60)
    print(answer_data["answer"])
    print("\n출처:")
    for src in answer_data["sources"]:
        print(f"  - {src['title']} (유사도: {src['score']})")

if __name__ == "__main__":
    asyncio.run(test_answer())
```

**실행:**
```bash
python tests/test_answer.py
```

**결과 예시:**
```
🔍 검색 중: 연차 휴가 신청 방법은?
🤖 GPT 답변 생성 중...

============================================================
질문: 연차 휴가 신청 방법은?
============================================================
연차 휴가는 근태 관리 시스템에서 최소 3일 전에 신청해야 합니다. 
입사 1년 후부터 15일이 부여되며, 미사용 연차는 익년 상반기까지 이월 가능합니다.

**출처:**
- 인사규정.pdf 참고
- 복리후생 가이드.pdf 참고

출처:
  - sample.pdf (유사도: 0.89)
  - sample.pdf (유사도: 0.82)
  - sample.pdf (유사도: 0.76)
```

---

### Step 8: FastAPI 서버 구성

**파일 생성:** `app/main.py`

```python
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from app.vector_store import search_documents
from app.llm import generate_answer
import uvicorn

app = FastAPI(title="RAG 챗봇 API")

class QuestionRequest(BaseModel):
    question: str

@app.get("/")
def health_check():
    return {"status": "ok", "message": "RAG 챗봇 서버 실행 중"}

@app.post("/ask")
async def ask_question(request: QuestionRequest):
    """
    질문에 답변하기
    """
    try:
        # 1. 벡터 검색
        results = search_documents(request.question, k=5)
        
        # 2. GPT 답변 생성
        answer_data = await generate_answer(request.question, results)
        
        return JSONResponse(content=answer_data)
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**서버 실행:**
```bash
python app/main.py
```

**브라우저에서 테스트:**
1. http://localhost:8000 접속 → `{"status": "ok"}` 확인
2. http://localhost:8000/docs 접속 → Swagger UI로 `/ask` 테스트

---

## ❌ 자주 만나는 에러와 해결법

### 에러 1: `ModuleNotFoundError: No module named 'app'`

**원인:** Python이 프로젝트 루트를 찾지 못함

**해결:**
```bash
# 방법 1: PYTHONPATH 설정 (추천)
export PYTHONPATH="${PYTHONPATH}:$(pwd)"  # Mac/Linux
set PYTHONPATH=%PYTHONPATH%;%CD%  # Windows

# 방법 2: 모듈로 실행
python -m tests.test_parser
```

---

### 에러 2: `openai.error.AuthenticationError`

**원인:** API 키가 잘못됨

**해결:**
1. `.env` 파일에서 `OPENAI_API_KEY` 확인
2. https://platform.openai.com/api-keys 에서 키 재발급
3. 키 앞뒤 공백 제거 확인
4. 서버 재시작 필수!

---

### 에러 3: `ImportError: cannot import name 'OpenAIEmbeddings'`

**원인:** LangChain 버전 불일치

**해결:**
```bash
pip uninstall langchain langchain-openai -y
pip install langchain==0.1.0 langchain-openai==0.0.2
```

---

### 에러 4: 검색 결과가 비어있음 (빈 배열)

**원인:** 
- 벡터 DB가 비어있거나
- `score_threshold`가 너무 높음

**해결:**
```python
# app/vector_store.py에서 임계치 낮추기
results = vector_client.similarity_search_with_relevance_scores(
    query=query,
    k=k,
    score_threshold=0.5  # 0.75 → 0.5로 낮춤
)
```

**디버깅:**
```python
# 벡터 DB에 데이터가 있는지 확인
print(f"색인된 문서 수: {vector_client._collection.count()}")
```

---

### 에러 5: PDF 파싱 시 한글 깨짐

**원인:** PDF 인코딩 문제

**해결:**
```python
# app/parsers/pdf.py 수정
text = "\n\n".join(
    page.extract_text(extraction_mode="layout")  # layout 모드 추가
    for page in reader.pages
)
```

**대안:** `pdfplumber` 사용
```bash
pip install pdfplumber
```

```python
import pdfplumber

def parse_pdf(file_path):
    with pdfplumber.open(file_path) as pdf:
        text = "\n\n".join(page.extract_text() for page in pdf.pages)
    ...
```


---

## ✅ 단계별 체크리스트

### Week 1: 기본 파이프라인 구축

**Step 1-2: 환경 설정 (30분)**
- [ ] 프로젝트 폴더 생성 완료 (`app/`, `data/`, `tests/` 등)
- [ ] 가상환경 활성화 확인 (프롬프트에 `(.venv)` 표시)
- [ ] `requirements.txt` 설치 완료 (에러 없음)
- [ ] `.env` 파일 생성 및 `OPENAI_API_KEY` 입력

**Step 3-4: 문서 파서 (1시간)**
- [ ] `app/parsers/pdf.py` 작성
- [ ] `tests/test_parser.py` 실행 성공
- [ ] 샘플 PDF(10페이지 이상) 준비 및 `data/` 폴더에 배치
- [ ] 파싱된 텍스트 1,000자 이상 확인

**Step 5: 청크 분할 (30분)**
- [ ] `app/pipelines.py` 작성
- [ ] `tests/test_chunking.py` 실행 → 청크 개수 10개 이상
- [ ] 청크 오버랩 확인 (청크1 끝 50자가 청크2 시작에 포함)

**Step 6: 벡터 DB 색인 (1시간)**
- [ ] `app/vector_store.py` 작성
- [ ] `tests/test_full_pipeline.py` 실행 → "색인 완료" 메시지
- [ ] `chroma/` 폴더 생성 확인 (파일 크기 100KB 이상)
- [ ] 검색 테스트 → 유사도 0.7 이상 문서 3개 이상 발견

**Step 7-8: GPT 답변 & API (2시간)**
- [ ] `app/llm.py` 작성
- [ ] `tests/test_answer.py` 실행 → 출처 포함된 답변 생성
- [ ] `app/main.py` 작성 및 서버 실행 (`python app/main.py`)
- [ ] http://localhost:8000/docs 접속 → Swagger UI 확인
- [ ] `/ask` 엔드포인트 테스트 → 200 OK 응답

---

### Week 2-3: 데모 준비 (챗봇 연동 전)

- [ ] 웹 데모 UI 작성 (`web/index.html`)
- [ ] 에러 처리 테스트 (API 키 없을 때, 문서 없을 때)
- [ ] 스크린샷 10장 이상 촬영 (정상 응답, 에러, 출처 표시)
- [ ] GitHub에 코드 업로드 (`.env`는 제외!)

---

### 최종 검증 (프리랜서 준비)

**기술 검증**
- [ ] 다른 PDF 3개로 재테스트 → 모두 정상 색인
- [ ] 5가지 질문 테스트 → 정확한 출처 표시
- [ ] 응답 시간 10초 이하 (검색 + GPT)
- [ ] 비용 계산 정확 (OpenAI 대시보드와 일치)

**데모 자료**
- [ ] 1분 데모 영상 촬영 (업로드 → 질문 → 답변 출처)
- [ ] 노션 소개 페이지 작성 ("RAG 챗봇 포트폴리오")
- [ ] GitHub README에 설치/실행 가이드 작성

**영업 준비**
- [ ] 제안서 템플릿 작성 (비용: 800~2,000만원)
- [ ] 기술 스택 설명 자료 (비개발자도 이해 가능하게)
- [ ] FAQ 10개 준비 ("할루시네이션 방지는?", "비용은 얼마?")

---

### 🚨 필수 확인 사항

**보안**
- [ ] `.gitignore`에 `.env`, `chroma/`, `logs/` 추가
- [ ] GitHub에 API 키가 노출되지 않았는지 재확인
- [ ] 데모 영상에 실제 회사 문서 노출 안 됨

**비용**
- [ ] OpenAI 사용량 알림 설정 (월 10달러 초과 시 이메일)
- [ ] 테스트 시 문서 10개 이하로 제한 (임베딩 비용 절감)

**품질**
- [ ] 5가지 이상의 질문으로 정확도 테스트
- [ ] 출처가 없는 답변은 반환하지 않는지 확인
- [ ] 한글 문서 파싱 정상 (깨짐 없음)

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

## 🎓 다음 단계는?

### Week 2: 텔레그램 챗봇 연동
→ [`implementation/bots.md`](bots.md)로 이동

**배울 내용:**
- BotFather로 봇 생성
- Webhook 설정 (ngrok 사용)
- 텔레그램 메시지 포맷 변환
- 1분 데모 영상 촬영

---

### Week 3: 웹 데모 UI
→ [`implementation/web-admin.md`](web-admin.md)로 이동

**배울 내용:**
- HTML + Vanilla JS로 깔끔한 UI
- 로딩 스피너 & 에러 토스트
- 출처 링크 카드
- 스크린샷 10장 확보

---

### Week 4-6: 품질 & 운영
→ [`roadmap/week01-08.md`](../roadmap/week01-08.md)로 이동

**배울 내용:**
- 정확도 평가 (RAGAS)
- 권한 관리 (JWT)
- 비용/로그 모니터링
- 관리자 대시보드

---

### Week 7-8: 배포 & 영업
→ [`business/package.md`](../business/package.md)로 이동

**배울 내용:**
- Docker 배포
- 가격 패키지 구성
- 제안서 작성
- 계약서 템플릿

---

## 💼 프리랜서 생존 팁

### 첫 외주를 따내는 법

**1. 포트폴리오 3종 세트**
```
✅ GitHub 리포지토리 (코드 + README)
✅ 노션 소개 페이지 (비개발자용)
✅ 1분 데모 영상 (YouTube 비공개)
```

**2. 제안서 작성 예시**
```markdown
[회사명] 귀하

안녕하세요, RAG 챗봇 전문 개발자 [이름]입니다.

귀사의 [문제 상황 - 예: 200페이지 규정집 검색 어려움]을 
AI 챗봇으로 해결하는 솔루션을 제안드립니다.

📌 해결 방안:
- PDF 업로드 → 자동 색인
- 질문 시 출처 페이지 번호 표시
- 텔레그램/웹 멀티 채널 지원

💰 예상 비용: 1,200만원 (4주 개발 + 2주 테스트)
📅 일정: 계약 후 6주
🎬 데모: [YouTube 링크]

감사합니다.
```

**3. 단가 협상 가이드**
| 구분      | 금액          | 근거                           |
| --------- | ------------- | ------------------------------ |
| 최소 견적 | 800만원       | 개발 4주 (주 200만원)          |
| 표준 견적 | 1,200만원     | 개발 + 테스트 + 문서화         |
| 고급 견적 | 2,000만원     | 권한 관리 + 관리자 페이지 포함 |
| 유지보수  | 월 50~200만원 | 문서 업데이트, 버그 수정       |

---

## 📚 참고 자료

### 공식 문서
- [LangChain 텍스트 분할](https://python.langchain.com/docs/modules/data_connection/document_transformers/)
- [Chroma 문서](https://docs.trychroma.com/)
- [OpenAI 가격표](https://openai.com/pricing)
- [FastAPI 튜토리얼](https://fastapi.tiangolo.com/tutorial/)

### 추천 학습
- [RAG 개념 영상 (YouTube)](https://youtube.com) - "Retrieval Augmented Generation 설명"
- [LangChain Cookbook](https://python.langchain.com/cookbook) - 실전 예제
- [Chroma 튜토리얼](https://docs.trychroma.com/getting-started) - 10분 입문

### 문제 해결
- [`appendix/troubleshooting.md`](../appendix/troubleshooting.md) - 자주 묻는 질문
- GitHub Discussions - 커뮤니티 질문
- Stack Overflow #langchain #rag

---

## 🏆 마지막 당부

**초보자가 가장 많이 하는 실수:**

1. ❌ **코드만 작성하고 테스트 안 함**
   - ✅ 각 Step마다 반드시 테스트 파일 실행하기

2. ❌ **문서 하나로만 테스트**
   - ✅ 최소 3가지 종류의 문서로 검증 (PDF, Docx, 한글/영문)

3. ❌ **에러 나면 포기**
   - ✅ "자주 만나는 에러" 섹션 먼저 확인 후 구글링

4. ❌ **완벽하게 만들려고 함**
   - ✅ Week 1에는 "작동만 하면 OK" → 나중에 리팩토링

5. ❌ **혼자 끙끙 앓음**
   - ✅ GitHub Discussions나 카카오톡 오픈채팅으로 질문

---

**🎉 여기까지 왔다면, 당신은 이미 80%의 개발자를 앞섰습니다!**

다음 주차로 넘어가기 전에:
- [ ] 체크리스트 재확인
- [ ] GitHub에 코드 푸시
- [ ] 노션에 학습 일지 기록

**다음 단계:** [`implementation/bots.md`](bots.md)에서 텔레그램 챗봇을 만들어 봅시다! 🚀

