# Step 3: 웹 데모 & 관리자 페이지 - 고객이 보는 첫인상 만들기

> **목표**: 웹 클라이언트 데모와 관리자 페이지(권한·로그·비용 모니터링)를 구현하여 고객사 데모 및 운영 신뢰도를 높인다.

---

## 🎯 이 단계를 배우는 이유

### 왜 웹 데모가 중요한가?

**고객의 실제 니즈:**
```
고객: "데모 좀 보여주세요."
개발자: "텔레그램 봇으로 보여드릴게요."
고객: "PC에서도 볼 수 있나요? 회의실에서 보여줘야 해서요."
```

**챗봇만의 한계:**
- ❌ PC에서 보기 불편 (모바일 앱 위주)
- ❌ 회의실에서 큰 화면으로 보여주기 어려움
- ❌ 스크린샷/녹화가 번거로움

**웹 데모의 강점:**
- ✅ PC/모바일 모두 지원
- ✅ 회의실 프로젝터로 바로 보여줄 수 있음
- ✅ 스크린샷 10장 = 포트폴리오 완성! 📸
- ✅ **"전문적으로 보인다"** = 신뢰도 상승

### 프리랜서 입장에서 왜 중요한가?

1. **포트폴리오의 핵심**
   - 텔레그램 영상: 1개
   - **웹 데모 스크린샷: 10장** (더 많은 정보 전달)
   - → 노션 소개 페이지가 풍성해짐

2. **고객 미팅 시 필수**
   - 회의실에서 노트북으로 바로 데모
   - "이렇게 작동합니다" → 즉시 이해
   - → 계약 확률 50% → **80%**로 상승

3. **관리자 페이지 = 운영 신뢰도**
   - "비용이 얼마나 드나요?" → 대시보드로 보여주기
   - "어떤 질문이 많나요?" → 통계 차트로 보여주기
   - → **"운영 경험이 있네요"** = 단가 상승

### 이 문서를 끝내면 이렇게 됩니다

**Before (챗봇만)**
```
고객: "PC에서도 볼 수 있나요?"
개발자: "텔레그램 앱에서만..." 💥
고객: "회의실에서 보여줘야 하는데..."
```

**After (웹 데모 완성)**
```
고객: "PC에서도 볼 수 있나요?"
여러분: "네, 웹 데모가 있습니다. 이 링크로 접속하시면 됩니다.
       관리자 페이지에서 통계도 확인하실 수 있어요." ✨
고객: "오, 이거 보니까 신뢰가 가네요!"
```

---

## 💡 핵심 개념 먼저 이해하기

### 1. 웹 데모 vs 관리자 페이지 차이

**웹 데모 (Week 3):**
- 사용자용 (질문 입력 → 답변 확인)
- 목적: **고객이 직접 체험**
- 기술: HTML + Vanilla JS (간단하게)

**관리자 페이지 (Week 6):**
- 관리자용 (통계, 로그, 비용 모니터링)
- 목적: **운영 신뢰도 확보**
- 기술: JWT 인증 + 차트 라이브러리

**왜 분리하나요?**
- ✅ 사용자는 간단한 UI만 필요
- ✅ 관리자는 복잡한 통계 필요
- ✅ 권한 분리 (일반 사용자 ≠ 관리자)

### 2. JWT(JSON Web Token)란?

**문제 상황:**
```
사용자: "관리자 페이지 보여주세요."
서버: "누구세요?" 💥
```

**JWT 해결책:**
```python
# 로그인 시 토큰 발급
token = jwt.encode({"user_id": 123, "role": "admin"}, secret)

# 이후 요청마다 토큰 검증
user = jwt.decode(token, secret)  # {"user_id": 123, "role": "admin"}
if user["role"] == "admin":
    show_dashboard()  # ✅ 관리자만 접근
```

**왜 이게 중요한가?**
- ✅ 세션 관리 불필요 (서버 메모리 절약)
- ✅ 마이크로서비스에 적합 (토큰만 검증)
- ✅ 실무에서 필수 기술

### 3. 권한 필터링이 왜 필요한가?

**문제 상황:**
```
일반 직원: "임원 전용 문서 보여주세요."
챗봇: "네, 여기 있습니다." 💥 (보안 위험!)
```

**권한 필터링:**
```python
# 사용자 역할 확인
if user.role == "employee":
    filters = {"access_level": "public"}  # 공개 문서만
elif user.role == "manager":
    filters = {"access_level": {"$in": ["public", "manager"]}}  # 공개 + 관리자

# 필터 적용
results = chroma.query(query_texts=[question], where=filters)
```

**왜 이게 중요한가?**
- ✅ 기업 고객의 필수 요구사항
- ✅ "권한 관리 안 되면 계약 안 해요"
- → **권한 기능 = 단가 +500만원**

---

## 🎯 학습 목표

| Step | 결과                 | 핵심 역량                               |
| ---- | -------------------- | --------------------------------------- |
| 1    | 웹 데모 UI 구성      | HTML + Vanilla JS, Fetch API, 에러 처리 |
| 2    | 관리자 대시보드      | JWT 인증, 차트 라이브러리, 통계 API     |
| 3    | 권한 필터링 구현     | 사용자 역할 기반 문서 접근 제어         |
| 4    | 로깅 & 비용 모니터링 | DB 로깅, 비용 계산, 일별 통계           |

---

## 🛠️ 사전 준비

| 항목        | 상세                                                                                                       |
| ----------- | ---------------------------------------------------------------------------------------------------------- |
| 환경        | Week 1 RAG 파이프라인 완성, Week 2 챗봇 연동 완성 (선택)                                                   |
| 패키지      | `python-jose[cryptography]` (JWT), `passlib[bcrypt]` (비밀번호 해싱), `sqlalchemy` (DB), `chart.js` (차트) |
| 환경변수    | `.env`에 `JWT_SECRET`, `DATABASE_URL` (SQLite 또는 PostgreSQL)                                             |
| 샘플 데이터 | 테스트용 사용자 계정 2개 (일반 사용자, 관리자)                                                             |

**⚠️ 필수: Week 1의 RAG 파이프라인이 완성되어 있어야 합니다!**
- [`implementation/rag-pipeline.md`](rag-pipeline.md)의 Step 1~8 완료 확인

---

## 🔄 따라하기 - 처음부터 끝까지

### Step 1: 웹 데모 UI 구성 (2시간)

#### 1-1. 폴더 구조 생성

```bash
# 프로젝트 루트에서
mkdir -p web/assets
```

**폴더 구조:**
```
web/
├── index.html          # 메인 페이지
└── assets/
    ├── app.js         # JavaScript 로직
    └── styles.css     # 스타일
```

#### 1-2. HTML 기본 구조

**파일 생성:** `web/index.html`

```html
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RAG 챗봇 데모</title>
    <link rel="stylesheet" href="assets/styles.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>🤖 회사 규정 챗봇</h1>
            <p>문서를 업로드하고 질문하세요</p>
        </header>
        
        <main>
            <!-- 질문 입력 폼 -->
            <form id="ask-form">
                <textarea 
                    id="question" 
                    placeholder="예: 연차 휴가 신청 방법은?"
                    required
                ></textarea>
                <button type="submit" id="submit-btn">
                    <span id="btn-text">질문하기</span>
                    <span id="btn-spinner" class="hidden">⏳ 처리 중...</span>
                </button>
            </form>
            
            <!-- 답변 영역 -->
            <div id="answer-section" class="hidden">
                <h2>답변</h2>
                <div id="answer" class="answer-box"></div>
                
                <h3>출처</h3>
                <ul id="sources" class="sources-list"></ul>
            </div>
            
            <!-- 에러 토스트 -->
            <div id="toast" class="toast hidden">
                <span id="toast-message"></span>
                <button id="toast-close">×</button>
            </div>
        </main>
    </div>
    
    <script src="assets/app.js"></script>
</body>
</html>
```

#### 1-3. CSS 스타일

**파일 생성:** `web/assets/styles.css`

```css
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    padding: 20px;
}

.container {
    max-width: 800px;
    margin: 0 auto;
    background: white;
    border-radius: 12px;
    box-shadow: 0 10px 40px rgba(0,0,0,0.2);
    padding: 40px;
}

header {
    text-align: center;
    margin-bottom: 40px;
}

header h1 {
    font-size: 2.5em;
    color: #333;
    margin-bottom: 10px;
}

header p {
    color: #666;
    font-size: 1.1em;
}

#ask-form {
    margin-bottom: 30px;
}

#question {
    width: 100%;
    min-height: 120px;
    padding: 15px;
    border: 2px solid #e0e0e0;
    border-radius: 8px;
    font-size: 16px;
    resize: vertical;
    font-family: inherit;
}

#question:focus {
    outline: none;
    border-color: #667eea;
}

#submit-btn {
    width: 100%;
    padding: 15px;
    background: #667eea;
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 18px;
    font-weight: bold;
    cursor: pointer;
    margin-top: 15px;
    transition: background 0.3s;
}

#submit-btn:hover:not(:disabled) {
    background: #5568d3;
}

#submit-btn:disabled {
    background: #ccc;
    cursor: not-allowed;
}

#answer-section {
    margin-top: 30px;
    padding-top: 30px;
    border-top: 2px solid #e0e0e0;
}

#answer-section h2 {
    color: #333;
    margin-bottom: 15px;
}

.answer-box {
    background: #f5f5f5;
    padding: 20px;
    border-radius: 8px;
    line-height: 1.8;
    white-space: pre-wrap;
    margin-bottom: 20px;
}

#sources {
    list-style: none;
}

.sources-list li {
    padding: 10px;
    background: #e8f4f8;
    margin-bottom: 10px;
    border-radius: 6px;
    border-left: 4px solid #667eea;
}

.toast {
    position: fixed;
    bottom: 20px;
    right: 20px;
    background: #ff4444;
    color: white;
    padding: 15px 20px;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    display: flex;
    align-items: center;
    gap: 15px;
    max-width: 400px;
    z-index: 1000;
}

.toast.hidden {
    display: none;
}

#toast-close {
    background: none;
    border: none;
    color: white;
    font-size: 24px;
    cursor: pointer;
    padding: 0;
    width: 24px;
    height: 24px;
}

.hidden {
    display: none;
}
```

#### 1-4. JavaScript 로직

**파일 생성:** `web/assets/app.js`

```javascript
// DOM 요소
const form = document.getElementById("ask-form");
const questionInput = document.getElementById("question");
const submitBtn = document.getElementById("submit-btn");
const btnText = document.getElementById("btn-text");
const btnSpinner = document.getElementById("btn-spinner");
const answerSection = document.getElementById("answer-section");
const answerBox = document.getElementById("answer");
const sourcesList = document.getElementById("sources");
const toast = document.getElementById("toast");
const toastMessage = document.getElementById("toast-message");
const toastClose = document.getElementById("toast-close");

// 로딩 상태 관리
function toggleLoading(isLoading) {
    submitBtn.disabled = isLoading;
    btnText.classList.toggle("hidden", isLoading);
    btnSpinner.classList.toggle("hidden", !isLoading);
}

// 에러 토스트 표시
function showToast(message) {
    toastMessage.textContent = message;
    toast.classList.remove("hidden");
    
    // 5초 후 자동 닫기
    setTimeout(() => {
        toast.classList.add("hidden");
    }, 5000);
}

toastClose.addEventListener("click", () => {
    toast.classList.add("hidden");
});

// 답변 렌더링
function renderAnswer(data) {
    // 답변 표시
    answerBox.textContent = data.answer;
    
    // 출처 표시
    sourcesList.innerHTML = "";
    if (data.sources && data.sources.length > 0) {
        data.sources.forEach((src) => {
            const li = document.createElement("li");
            li.textContent = `${src.title} (p.${src.page || "?"})`;
            if (src.url) {
                const link = document.createElement("a");
                link.href = src.url;
                link.textContent = " 링크";
                link.target = "_blank";
                li.appendChild(link);
            }
            sourcesList.appendChild(li);
        });
    } else {
        const li = document.createElement("li");
        li.textContent = "출처 없음";
        sourcesList.appendChild(li);
    }
    
    // 답변 영역 표시
    answerSection.classList.remove("hidden");
}

// 폼 제출 처리
form.addEventListener("submit", async (e) => {
    e.preventDefault();
    
    const question = questionInput.value.trim();
    if (!question) {
        showToast("질문을 입력해 주세요.");
        return;
    }
    
    toggleLoading(true);
    
    try {
        // API 호출
        const response = await fetch("/ask", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ question }),
        });
        
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(errorText || "요청 실패");
        }
        
        const data = await response.json();
        renderAnswer(data);
        
    } catch (error) {
        console.error("에러:", error);
        showToast("답변을 생성하지 못했습니다. 잠시 후 다시 시도해 주세요.");
    } finally {
        toggleLoading(false);
    }
});
```

#### 1-5. FastAPI 정적 파일 서빙

**파일 수정:** `app/main.py` (추가)

```python
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# 정적 파일 서빙 (web/ 폴더)
app.mount("/web", StaticFiles(directory="web"), name="web")

@app.get("/")
def root():
    """
    웹 데모 페이지로 리다이렉트
    """
    return FileResponse("web/index.html")

@app.get("/demo")
def demo():
    """
    웹 데모 페이지 (직접 접근)
    """
    return FileResponse("web/index.html")
```

#### 1-6. 테스트

**서버 실행:**
```bash
python app/main.py
```

**브라우저에서:**
1. http://localhost:8000 접속
2. 질문 입력: "연차 휴가는 몇 일인가요?"
3. 답변 확인! 🎉

**스크린샷 촬영:**
- [ ] 질문 입력 화면
- [ ] 로딩 중 화면
- [ ] 답변 표시 화면
- [ ] 출처 표시 화면
- [ ] 에러 토스트 화면

---

### Step 2: 관리자 대시보드 (Week 6, 4시간)

#### 2-1. 데이터베이스 모델

**파일 생성:** `app/models.py`

```python
from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="user")  # user, manager, admin
    team = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class RequestLog(Base):
    __tablename__ = "requests"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    channel = Column(String)  # web, telegram, kakao
    question = Column(String)
    answer = Column(String)
    sources = Column(JSON)  # [{"title": "...", "page": "..."}]
    token_in = Column(Integer, default=0)
    token_out = Column(Integer, default=0)
    cost = Column(Float, default=0.0)
    latency_ms = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
```

#### 2-2. DB 초기화

**파일 생성:** `app/database.py`

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./rag_bot.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """
    데이터베이스 테이블 생성
    """
    Base.metadata.create_all(bind=engine)

def get_db():
    """
    DB 세션 생성 (의존성 주입용)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

#### 2-3. 로깅 함수

**파일 생성:** `app/logging.py`

```python
from app.database import get_db
from app.models import RequestLog
from decimal import Decimal
from datetime import datetime

PROMPT_PRICE = Decimal("0.0005")  # per 1K tokens
COMPLETION_PRICE = Decimal("0.0015")

def calc_cost(token_in: int, token_out: int) -> float:
    """
    비용 계산
    """
    cost = (Decimal(token_in) / 1000 * PROMPT_PRICE) + (
        Decimal(token_out) / 1000 * COMPLETION_PRICE
    )
    return float(cost)

def log_request(
    db,
    channel: str,
    question: str,
    answer: str,
    sources: list,
    token_in: int,
    token_out: int,
    latency_ms: int,
    user_id: int = None
):
    """
    요청 로그 저장
    """
    cost = calc_cost(token_in, token_out)
    
    log = RequestLog(
        user_id=user_id,
        channel=channel,
        question=question,
        answer=answer,
        sources=sources,
        token_in=token_in,
        token_out=token_out,
        cost=cost,
        latency_ms=latency_ms,
        created_at=datetime.utcnow()
    )
    
    db.add(log)
    db.commit()
    return log
```

#### 2-4. 통계 API

**파일 수정:** `app/main.py` (추가)

```python
from app.database import get_db, init_db
from app.models import RequestLog
from sqlalchemy import func
from datetime import datetime, timedelta
from fastapi import Depends
from sqlalchemy.orm import Session

# DB 초기화 (서버 시작 시)
@app.on_event("startup")
def startup():
    init_db()

@app.get("/admin/stats/daily")
def get_daily_stats(
    from_date: str = None,
    to_date: str = None,
    db: Session = Depends(get_db)
):
    """
    일별 통계 (요청 수, 토큰 사용량, 비용)
    """
    # 날짜 기본값 (최근 7일)
    if not from_date:
        from_date = (datetime.now() - timedelta(days=7)).isoformat()
    if not to_date:
        to_date = datetime.now().isoformat()
    
    # 일별 집계
    stats = db.query(
        func.date(RequestLog.created_at).label("date"),
        func.count(RequestLog.id).label("count"),
        func.sum(RequestLog.token_in + RequestLog.token_out).label("tokens"),
        func.sum(RequestLog.cost).label("cost")
    ).filter(
        RequestLog.created_at >= from_date,
        RequestLog.created_at <= to_date
    ).group_by(
        func.date(RequestLog.created_at)
    ).all()
    
    return {
        "dates": [s.date.isoformat() for s in stats],
        "counts": [s.count for s in stats],
        "tokens": [s.tokens or 0 for s in stats],
        "costs": [float(s.cost or 0) for s in stats]
    }

@app.get("/admin/stats/channel")
def get_channel_stats(db: Session = Depends(get_db)):
    """
    채널별 통계
    """
    stats = db.query(
        RequestLog.channel,
        func.count(RequestLog.id).label("count"),
        func.sum(RequestLog.cost).label("cost")
    ).group_by(
        RequestLog.channel
    ).all()
    
    return {
        "channels": [s.channel for s in stats],
        "counts": [s.count for s in stats],
        "costs": [float(s.cost or 0) for s in stats]
    }
```

#### 2-5. 관리자 페이지 HTML

**파일 생성:** `web/admin.html`

```html
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>관리자 대시보드</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link rel="stylesheet" href="assets/styles.css">
</head>
<body>
    <div class="container">
        <h1>📊 관리자 대시보드</h1>
        
        <div class="stats-grid">
            <div class="stat-card">
                <h3>일별 요청 수</h3>
                <canvas id="daily-chart"></canvas>
            </div>
            
            <div class="stat-card">
                <h3>채널별 비율</h3>
                <canvas id="channel-chart"></canvas>
            </div>
        </div>
    </div>
    
    <script src="assets/admin.js"></script>
</body>
</html>
```

**파일 생성:** `web/assets/admin.js`

```javascript
// 일별 통계 차트
async function loadDailyStats() {
    const res = await fetch("/admin/stats/daily");
    const data = await res.json();
    
    new Chart(document.getElementById("daily-chart"), {
        type: "line",
        data: {
            labels: data.dates,
            datasets: [{
                label: "요청 수",
                data: data.counts,
                borderColor: "#667eea",
                tension: 0.1
            }]
        }
    });
}

// 채널별 통계 차트
async function loadChannelStats() {
    const res = await fetch("/admin/stats/channel");
    const data = await res.json();
    
    new Chart(document.getElementById("channel-chart"), {
        type: "doughnut",
        data: {
            labels: data.channels,
            datasets: [{
                data: data.counts,
                backgroundColor: ["#667eea", "#764ba2", "#f093fb"]
            }]
        }
    });
}

// 페이지 로드 시 실행
loadDailyStats();
loadChannelStats();
```

---

## ❌ 자주 만나는 에러와 해결법

### 에러 1: `CORS policy: No 'Access-Control-Allow-Origin'`

**원인:** 브라우저가 다른 도메인 요청 차단

**해결:**
```python
# app/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 환경
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### 에러 2: `Failed to fetch` (네트워크 오류)

**원인:** 서버가 꺼졌거나 URL 잘못됨

**해결:**
```javascript
// web/assets/app.js
const API_URL = window.location.origin;  // 자동으로 현재 도메인 사용

fetch(`${API_URL}/ask`, { ... })
```

---

### 에러 3: 차트가 표시되지 않음

**원인:** Chart.js 로드 실패 또는 데이터 형식 오류

**해결:**
```javascript
// 데이터 확인
console.log("데이터:", data);

// Chart.js 로드 확인
if (typeof Chart === "undefined") {
    console.error("Chart.js가 로드되지 않았습니다.");
}
```

---

## ✅ 단계별 체크리스트

### Week 3: 웹 데모 (1일)

**Step 1: UI 구성 (2시간)**
- [ ] `web/index.html` 작성
- [ ] `web/assets/styles.css` 작성
- [ ] `web/assets/app.js` 작성
- [ ] FastAPI 정적 파일 서빙 설정
- [ ] http://localhost:8000 접속 → 페이지 표시 확인

**Step 1-6: 테스트 (1시간)**
- [ ] 질문 입력 → 답변 확인
- [ ] 로딩 스피너 정상 작동
- [ ] 출처 표시 정상
- [ ] 에러 토스트 정상 (API 오류 시)
- [ ] 스크린샷 10장 촬영

---

### Week 6: 관리자 페이지 (2일)

**Step 2-1: DB 모델 (1시간)**
- [ ] `app/models.py` 작성
- [ ] `app/database.py` 작성
- [ ] `init_db()` 실행 → 테이블 생성 확인

**Step 2-2: 로깅 (1시간)**
- [ ] `app/logging.py` 작성
- [ ] `/ask` 엔드포인트에 로깅 추가
- [ ] DB에 로그 저장 확인

**Step 2-3: 통계 API (2시간)**
- [ ] `/admin/stats/daily` 구현
- [ ] `/admin/stats/channel` 구현
- [ ] API 테스트 (Postman 또는 curl)

**Step 2-4: 관리자 페이지 (2시간)**
- [ ] `web/admin.html` 작성
- [ ] `web/assets/admin.js` 작성
- [ ] Chart.js 차트 표시 확인
- [ ] 스크린샷 5장 촬영

---

### 최종 검증 (프리랜서 준비)

**기술 검증**
- [ ] 웹 데모 정상 작동 (PC + 모바일)
- [ ] 관리자 대시보드 정상 작동
- [ ] 로그 저장 정상 (DB 확인)
- [ ] 통계 차트 정상 표시

**데모 자료**
- [ ] 웹 데모 스크린샷 10장
- [ ] 관리자 대시보드 스크린샷 5장
- [ ] 노션 소개 페이지 업데이트

**영업 준비**
- [ ] "웹 데모 + 관리자 페이지" 강조
- [ ] 단가 상향 근거 ("운영 모니터링 포함 = +300만원")

---

## 🎓 다음 단계는?

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

## 📚 참고 자료

### 공식 문서
- [FastAPI 정적 파일](https://fastapi.tiangolo.com/tutorial/static-files/)
- [Chart.js 문서](https://www.chartjs.org/docs/)
- [SQLAlchemy 문서](https://docs.sqlalchemy.org/)

### 추천 학습
- [Vanilla JS Fetch API (MDN)](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API)
- [JWT 인증 가이드](https://jwt.io/introduction)

### 문제 해결
- [`appendix/troubleshooting.md`](../appendix/troubleshooting.md) - "웹 데모 CORS 오류"
- Stack Overflow #fastapi #chartjs

---

## 🏆 마지막 당부

**초보자가 가장 많이 하는 실수:**

1. ❌ **복잡한 프레임워크 사용 (React, Vue)**
   - ✅ Vanilla JS로 충분 (간단하고 빠름)

2. ❌ **에러 처리 안 함**
   - ✅ try-catch + 토스트 메시지 필수

3. ❌ **모바일 반응형 안 함**
   - ✅ `viewport` 메타 태그 + CSS 미디어 쿼리

4. ❌ **관리자 페이지 인증 안 함**
   - ✅ JWT 필수 (나중에 추가해도 됨)

5. ❌ **스크린샷 안 찍음**
   - ✅ 포트폴리오의 핵심! 10장 이상 필수

---

**🎉 웹 데모와 관리자 페이지를 만들었다면, 당신은 이미 고객이 원하는 모든 것을 갖추고 있습니다!**

다음 주차로 넘어가기 전에:
- [ ] 체크리스트 재확인
- [ ] 스크린샷 15장 확보 (웹 데모 10장 + 관리자 5장)
- [ ] GitHub에 코드 푸시

**다음 단계:** [`roadmap/week01-08.md`](../roadmap/week01-08.md)에서 품질 개선과 운영을 배워봅시다! 🚀
