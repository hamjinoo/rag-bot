# Step 2: 텔레그램 & 카카오 챗봇 연동 - 고객이 바로 쓸 수 있는 채널 만들기

> **목표**: 동일한 RAG 파이프라인을 활용해 텔레그램과 카카오 i 오픈빌더 채널을 모두 지원한다.

---

## 🎯 이 단계를 배우는 이유

### 왜 챗봇 채널이 필요한가?

**고객의 실제 니즈:**
```
고객: "웹 데모는 좋은데, 우리 직원들은 카카오톡만 써요."
고객: "텔레그램으로도 되나요? 해외 팀이 많아서요."
고객: "모바일에서 바로 질문하고 싶어요."
```

**단순 웹 데모의 한계:**
- ❌ 모바일에서 URL 입력 불편
- ❌ 앱 설치 필요 없음 (채팅 앱은 이미 설치됨)
- ❌ 푸시 알림 불가 (웹은 새로고침해야 확인)

**챗봇 채널의 강점:**
- ✅ 카카오톡/텔레그램 앱에서 바로 사용
- ✅ 푸시 알림으로 답변 알림
- ✅ 대화 기록 자동 저장
- ✅ **고객이 "바로 쓸 수 있다"** = 외주 단가 상승! 💰

### 프리랜서 입장에서 왜 중요한가?

1. **경쟁력 차별화**
   - 대부분: "웹 데모만 제공"
   - **여러분**: "웹 + 텔레그램 + 카카오톡 3채널 지원" ✨
   - → 단가 1,200만원 → **1,800만원**으로 협상 가능

2. **실무 경험 증명**
   - Webhook, 시그니처 검증, 타임아웃 처리
   - → "운영 경험이 있네요" = 신뢰도 상승

3. **데모 영상의 임팩트**
   - 웹 스크린샷: 3점/10점
   - **카카오톡에서 질문 → 답변 영상**: 9점/10점 🎬

### 이 문서를 끝내면 이렇게 됩니다

**Before (웹 데모만)**
```
고객: "카카오톡으로도 되나요?"
개발자: "아직 안 됩니다. 웹만..." 💥
고객: "그럼 다른 업체 찾아볼게요."
```

**After (챗봇 연동 완료)**
```
고객: "카카오톡으로도 되나요?"
여러분: "네, 텔레그램과 카카오톡 모두 지원합니다.
       데모 영상 보여드릴까요?" ✨
고객: "오, 바로 쓸 수 있네요! 계약 진행하겠습니다."
```

---

## 💡 핵심 개념 먼저 이해하기

### 1. Webhook이 뭐야?

**전통적인 방식 (Polling):**
```python
# 서버가 계속 물어봄 (비효율)
while True:
    updates = telegram.getUpdates()  # "새 메시지 있어요?"
    if updates:
        process(updates)
    time.sleep(1)  # 1초마다 확인
```

**Webhook 방식 (Push):**
```python
# 텔레그램이 우리 서버로 메시지 보냄 (효율적)
@app.post("/telegram/webhook")
async def webhook(update):
    # 메시지가 오면 자동으로 이 함수 실행
    process(update)
```

**비유:**
- Polling = "편지 왔나요?" 계속 물어보기
- Webhook = 우편함에 편지 오면 자동으로 알림

**왜 Webhook이 좋은가?**
- ✅ 실시간 응답 (1초 이내)
- ✅ 서버 부하 감소 (계속 물어볼 필요 없음)
- ✅ 비용 절감 (API 호출 횟수 1/100)

### 2. 시그니처 검증이 왜 필요한가?

**문제 상황:**
```
해커: "카카오톡인 척하고 악성 요청 보내기"
서버: "OK, 처리할게요" 💥
```

**시그니처 검증:**
```python
# 카카오가 보낸 요청인지 확인
signature = request.headers["X-Kakao-Signature"]
body = request.body

# 비밀키로 해시 생성
expected = hmac.new(secret, body, sha256)

# 일치하면 진짜 카카오, 아니면 해커
if expected == signature:
    process()  # ✅ 처리
else:
    return 403  # ❌ 거부
```

**왜 이게 중요한가?**
- ✅ 보안 필수 (해커가 악용 방지)
- ✅ 카카오 검수 통과 필수 조건
- ✅ 실무에서 반드시 구현해야 함

### 3. 텔레그램 vs 카카오 차이점

| 항목            | 텔레그램             | 카카오톡                    |
| --------------- | -------------------- | --------------------------- |
| **설정 난이도** | ⭐ 쉬움 (BotFather만) | ⭐⭐ 보통 (오픈빌더)          |
| **응답 시간**   | 5초 이내             | **3초 이내** (검수 기준)    |
| **포맷**        | Markdown 텍스트      | JSON (simpleText/basicCard) |
| **시그니처**    | 불필요               | **필수** (HMAC-SHA256)      |
| **타임아웃**    | 유연함               | 엄격함 (5초 초과 시 실패)   |
| **사용자층**    | 해외/IT 업계         | 한국 일반인                 |

**추천 순서:**
1. 텔레그램 먼저 (쉬움, 30분 완성)
2. 카카오톡 나중에 (검수 필요, 2시간)

---

## 🎯 학습 목표

| Step | 결과                    | 핵심 역량                                  |
| ---- | ----------------------- | ------------------------------------------ |
| 1    | 텔레그램 봇 웹훅 구성   | BotFather 설정, HTTPS Webhook, 메시지 포맷 |
| 2    | 카카오 스킬 서버 연동   | 시그니처 검증, JSON 변환, 타임아웃 대응    |
| 3    | 공통 서비스 레이어 설계 | 채널별 포맷터, `rag_service` 재사용        |
| 4    | 운영/보안 체크          | Rate limit, 금칙어, 로그/비용 모니터링     |

---

## 🛠️ 사전 준비

| 항목     | 상세                                                                                             |
| -------- | ------------------------------------------------------------------------------------------------ |
| 텔레그램 | BotFather 계정, 봇 토큰, HTTPS 도메인(ngrok 등)                                                  |
| 카카오   | 카카오톡 채널, 오픈빌더 프로젝트, 시그니처 비밀키                                                |
| 환경변수 | `.env`에 `TELEGRAM_BOT_TOKEN`, `TELEGRAM_WEBHOOK_URL`, `KAKAO_CHANNEL_SECRET`, `KAKAO_SKILL_URL` |
| 네트워크 | 200ms 이상 응답 지연 시 대비(타임아웃, 재시도)                                                   |

**⚠️ 필수: Week 1의 RAG 파이프라인이 완성되어 있어야 합니다!**
- [`implementation/rag-pipeline.md`](rag-pipeline.md)의 Step 1~8 완료 확인

---

## 🔄 따라하기 - 처음부터 끝까지

### Step 1: 텔레그램 봇 생성 (5분)

#### 1-1. BotFather에서 봇 만들기

**텔레그램 앱에서:**
1. 검색창에 `@BotFather` 입력
2. `/newbot` 명령어 전송
3. 봇 이름 입력 (예: "회사 규정 챗봇")
4. 봇 사용자명 입력 (예: `company_rag_bot` - 영어만, 끝에 `_bot` 필수)

**결과:**
```
BotFather: "Done! Use this token to access the HTTP API:
          123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
```

**이 토큰을 `.env`에 저장:**
```env
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
```

#### 1-2. Privacy 설정 (중요!)

**BotFather에게:**
```
/setprivacy
```

**봇 선택 → "Disable" 선택**

**왜 필요한가?**
- Enable: 봇이 `/start` 명령어를 받아야만 메시지 수신
- **Disable: 모든 메시지 자동 수신** (우리가 원하는 것)

---

### Step 2: ngrok으로 HTTPS 터널 생성 (10분)

**왜 필요한가?**
- 텔레그램 Webhook은 **HTTPS만** 허용
- 로컬 개발 환경(`localhost:8000`)은 HTTP
- → ngrok이 `https://xxx.ngrok.io`로 변환

#### 2-1. ngrok 설치

**Windows:**
1. https://ngrok.com/download 접속
2. `ngrok.exe` 다운로드
3. `C:\ngrok\ngrok.exe` 경로에 저장

**Mac:**
```bash
brew install ngrok
```

#### 2-2. FastAPI 서버 실행

```bash
# 터미널 1
python app/main.py
# → http://localhost:8000 실행 중
```

#### 2-3. ngrok 터널 시작

**Windows:**
```bash
# 터미널 2
C:\ngrok\ngrok.exe http 8000
```

**Mac/Linux:**
```bash
# 터미널 2
ngrok http 8000
```

**결과:**
```
Forwarding  https://abc123.ngrok.io -> http://localhost:8000
```

**이 URL을 `.env`에 저장:**
```env
TELEGRAM_WEBHOOK_URL=https://abc123.ngrok.io/telegram/webhook
```

**⚠️ 주의:**
- ngrok 무료 버전은 재시작 시 URL 변경됨
- 데모 전에 다시 확인 필수!

---

### Step 3: 텔레그램 Webhook 구현 (30분)

#### 3-1. 텔레그램 클라이언트 작성

**파일 생성:** `app/clients/telegram.py`

```python
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

async def send_message(chat_id: int, text: str):
    """
    텔레그램 메시지 전송
    
    Args:
        chat_id: 사용자 채팅 ID
        text: 전송할 텍스트 (Markdown 지원)
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_URL}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "Markdown",  # **굵게**, _기울임_ 지원
            }
        )
        return response.json()

async def send_typing(chat_id: int):
    """
    "입력 중..." 표시 (사용자 경험 향상)
    """
    async with httpx.AsyncClient() as client:
        await client.post(
            f"{API_URL}/sendChatAction",
            json={"chat_id": chat_id, "action": "typing"}
        )
```

#### 3-2. 메시지 포맷터 작성

**파일 생성:** `app/formatters/telegram.py`

```python
def format_answer(answer: str, sources: list[dict]) -> str:
    """
    RAG 답변을 텔레그램 Markdown 포맷으로 변환
    
    텔레그램 Markdown 규칙:
    - **굵게**: **text**
    - _기울임_: _text_
    - `코드`: `code`
    - [링크](url): [text](url)
    - 특수문자 이스케이프: _ → \_, * → \*
    """
    # 출처 목록 생성
    source_text = "\n\n*출처:*\n"
    for src in sources:
        title = src.get("title", "문서")
        page = src.get("page", "?")
        source_text += f"• {title} (p.{page})\n"
    
    # Markdown 특수문자 이스케이프
    answer = answer.replace("_", "\\_").replace("*", "\\*")
    
    return f"{answer}{source_text}"

def escape_markdown(text: str) -> str:
    """
    텔레그램 Markdown 특수문자 이스케이프
    """
    special = ["_", "*", "[", "]", "(", ")", "~", "`", ">", "#", "+", "-", "=", "|", "{", "}", ".", "!"]
    for char in special:
        text = text.replace(char, f"\\{char}")
    return text
```

#### 3-3. Webhook 엔드포인트 작성

**파일 수정:** `app/main.py`

```python
import warnings
import logging
import os
from fastapi import FastAPI, Request
from app.clients.telegram import send_message, send_typing
from app.formatters.telegram import format_answer
from app.vector_store import search_documents
from app.llm import generate_answer

# ChromaDB 텔레메트리 경고 무시
warnings.filterwarnings("ignore", category=UserWarning, module="chromadb")
warnings.filterwarnings("ignore", message=".*Failed to send telemetry event.*")
logging.getLogger("chromadb").setLevel(logging.ERROR)
os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")

app = FastAPI(title="RAG 챗봇 API")

@app.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    """
    텔레그램 Webhook 엔드포인트
    """
    try:
        update = await request.json()
        
        # 메시지 추출
        message = update.get("message") or {}
        chat_id = message.get("chat", {}).get("id")
        text = message.get("text", "").strip()
        
        if not text:
            return {"ok": True}
        
        # "입력 중..." 표시
        await send_typing(chat_id)
        
        # RAG 파이프라인 실행
        results = search_documents(text, k=5)
        answer_data = await generate_answer(text, results)
        
        # 텔레그램 포맷으로 변환
        formatted = format_answer(
            answer_data["answer"],
            answer_data["sources"]
        )
        
        # 메시지 전송
        await send_message(chat_id, formatted)
        
        return {"ok": True}
    
    except Exception as e:
        print(f"❌ 에러: {e}")
        import traceback
        traceback.print_exc()
        return {"ok": False, "error": str(e)}

@app.get("/")
def health_check():
    """헬스 체크 엔드포인트"""
    return {"status": "ok", "message": "RAG 챗봇 서버 실행 중"}

# 카카오 라우터는 아래 4-5 섹션 참조

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

#### 3-4. Webhook 등록

**터미널에서:**
```bash
# ngrok URL 확인 (터미널 2에서)
# 예: https://abc123.ngrok.io

# Webhook 등록
curl -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/setWebhook" \
  -H "Content-Type: application/json" \
  -d "{\"url\": \"$TELEGRAM_WEBHOOK_URL\"}"
```

**Windows CMD:**
```cmd
set TELEGRAM_BOT_TOKEN=123456789:ABC...
set TELEGRAM_WEBHOOK_URL=https://abc123.ngrok.io/telegram/webhook

curl -X POST "https://api.telegram.org/bot%TELEGRAM_BOT_TOKEN%/setWebhook" -H "Content-Type: application/json" -d "{\"url\": \"%TELEGRAM_WEBHOOK_URL%\"}"
```

**성공 확인:**
```bash
curl "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getWebhookInfo"
```

**결과 예시:**
```json
{
  "ok": true,
  "result": {
    "url": "https://abc123.ngrok.io/telegram/webhook",
    "has_custom_certificate": false,
    "pending_update_count": 0
  }
}
```

#### 3-5. 테스트

**텔레그램 앱에서:**
1. 봇 검색 (예: `@company_rag_bot`)
2. `/start` 전송
3. 질문 입력: "연차 휴가는 몇 일인가요?"
4. 답변 확인! 🎉

**예상 응답:**
```
연차 휴가는 입사 1년 후부터 15일이 부여됩니다.
근태 관리 시스템에서 최소 3일 전에 신청해야 합니다.

출처:
• 인사규정.pdf (p.3)
• 복리후생 가이드.pdf (p.5)
```

---

### Step 4: 카카오 i 오픈빌더 연동 (2시간)

#### 4-1. 카카오톡 채널 생성

1. https://developers.kakao.com 접속
2. 내 애플리케이션 → 애플리케이션 추가
3. 앱 이름 입력 (예: "회사 규정 챗봇")
4. **카카오톡 채널** 연결 (또는 새로 생성)

#### 4-2. 오픈빌더 프로젝트 생성

1. https://i.kakao.com 접속
2. 프로젝트 생성 → "스킬 서버" 선택
3. 스킬 서버 URL 입력: `https://abc123.ngrok.io/kakao/router`
4. **시그니처 비밀키 복사** → `.env`에 저장

```env
KAKAO_CHANNEL_SECRET=abc123def456...
KAKAO_SKILL_URL=https://abc123.ngrok.io/kakao/router
```

#### 4-3. 시그니처 검증 구현

**파일 생성:** `app/security/kakao.py`

```python
import base64
import hmac
import hashlib
import os
from dotenv import load_dotenv

load_dotenv()

SECRET = os.getenv("KAKAO_CHANNEL_SECRET")

def verify_signature(body: bytes, signature: str) -> bool:
    """
    카카오 요청 시그니처 검증
    
    Args:
        body: 요청 본문 (bytes)
        signature: X-Kakao-Signature 헤더 값
        
    Returns:
        True: 검증 성공, False: 검증 실패
    """
    if not SECRET:
        return False
    
    # HMAC-SHA256으로 해시 생성
    mac = hmac.new(
        SECRET.encode("utf-8"),
        body,
        hashlib.sha256
    )
    digest = base64.b64encode(mac.digest()).decode("utf-8")
    
    # 시그니처 비교 (타이밍 공격 방지)
    return hmac.compare_digest(digest, signature)
```

#### 4-4. 카카오 응답 포맷터

**파일 생성:** `app/formatters/kakao.py`

```python
def format_skill_response(answer: str, sources: list[dict]) -> dict:
    """
    RAG 답변을 카카오 스킬 응답 포맷으로 변환
    
    카카오 스킬 응답 형식:
    {
      "version": "2.0",
      "template": {
        "outputs": [
          {
            "simpleText": {
              "text": "답변 내용"
            }
          }
        ]
      }
    }
    """
    # 출처 목록 생성
    source_text = "\n\n📚 출처:\n"
    for src in sources:
        title = src.get("title", "문서")
        page = src.get("page", "?")
        source_text += f"• {title} (p.{page})\n"
    
    return {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": f"{answer}{source_text}"
                    }
                }
            ]
        }
    }

def format_error_response(error_msg: str) -> dict:
    """
    에러 응답 포맷
    """
    return {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": f"❌ {error_msg}\n\n잠시 후 다시 시도해 주세요."
                    }
                }
            ]
        }
    }
```

#### 4-5. 카카오 Webhook 엔드포인트

**파일 수정:** `app/main.py` (카카오 라우터 추가)

> **참고**: 이 코드는 기존 `app/main.py` 파일에 추가하는 것입니다. 텔레그램 webhook과 함께 사용할 수 있습니다.

```python
import asyncio
import json
from app.security.kakao import verify_signature
from app.formatters.kakao import format_skill_response, format_error_response

@app.post("/kakao/router")
async def kakao_router(request: Request):
    """
    카카오 i 오픈빌더 스킬 서버 엔드포인트
    """
    try:
        # 요청 본문 읽기 (시그니처 검증용)
        body = await request.body()
        
        # 시그니처 검증
        signature = request.headers.get("X-Kakao-Signature", "")
        if not verify_signature(body, signature):
            return {"error": "Invalid signature"}, 403
        
        # JSON 파싱 (body를 직접 파싱 - request.body() 후에는 request.json() 사용 불가)
        payload = json.loads(body.decode("utf-8"))
        
        # 사용자 질문 추출
        user_request = payload.get("userRequest", {})
        question = user_request.get("utterance", "").strip()
        
        if not question:
            return format_error_response("질문을 입력해 주세요.")
        
        # RAG 파이프라인 실행 (타임아웃 3초)
        results = search_documents(question, k=5)
        answer_data = await asyncio.wait_for(
            generate_answer(question, results),
            timeout=3.0  # 카카오는 5초 이내 응답 필수
        )
        
        # 카카오 포맷으로 변환
        return format_skill_response(
            answer_data["answer"],
            answer_data["sources"]
        )
    
    except asyncio.TimeoutError:
        return format_error_response("응답 시간이 초과되었습니다.")
    except Exception as e:
        print(f"❌ 에러: {e}")
        import traceback
        traceback.print_exc()
        return format_error_response("처리 중 오류가 발생했습니다.")
```

> **참고**: 서버 시작 코드(`if __name__ == "__main__":`)는 텔레그램 webhook 섹션(3-3)에 이미 포함되어 있습니다. 위 코드는 기존 `app/main.py` 파일에 추가하는 것입니다.

#### 4-6. 오픈빌더에서 테스트

1. 오픈빌더 → 테스트 채널 선택
2. "연차 휴가 신청 방법은?" 입력
3. 답변 확인! 🎉

**⚠️ 검수 전 체크리스트:**
- [ ] 응답 시간 5초 이내
- [ ] 시그니처 검증 정상 작동 (잘못된 요청 → 403)
- [ ] 에러 메시지 친절함 ("처리 중 오류" 등)
- [ ] 출처 표시 정확함

---

## ❌ 자주 만나는 에러와 해결법

### 에러 1: `Webhook was set, but HTTPS URL was not found`

**원인:** ngrok이 꺼졌거나 URL이 변경됨

**해결:**
```bash
# 1. ngrok 재시작
ngrok http 8000

# 2. 새 URL로 Webhook 재등록
curl -X POST "https://api.telegram.org/bot$TOKEN/setWebhook" \
  -d "{\"url\": \"https://새로운URL.ngrok.io/telegram/webhook\"}"
```

---

### 에러 2: `403 Forbidden` (카카오)

**원인:** 시그니처 검증 실패

**해결:**
```python
# app/security/kakao.py 디버깅
def verify_signature(body: bytes, signature: str) -> bool:
    # ... 기존 코드 ...
    
    # 디버깅 출력
    print(f"Expected: {digest}")
    print(f"Received: {signature}")
    
    return hmac.compare_digest(digest, signature)
```

**확인 사항:**
- `.env`의 `KAKAO_CHANNEL_SECRET` 정확한가?
- 요청 본문이 `bytes`로 전달되는가? (JSON 변환 전)
- `request.body()` 후에는 `request.json()`을 사용할 수 없으므로 `json.loads(body.decode("utf-8"))` 사용

---

### 에러 3: `Message is too long` (텔레그램)

**원인:** 텔레그램 메시지 제한 4,096자 초과

**해결:**
```python
# app/clients/telegram.py
async def send_message(chat_id: int, text: str):
    MAX_LENGTH = 4096
    
    if len(text) <= MAX_LENGTH:
        await _send(chat_id, text)
    else:
        # 메시지 분할
        chunks = [text[i:i+MAX_LENGTH] for i in range(0, len(text), MAX_LENGTH)]
        for chunk in chunks:
            await _send(chat_id, chunk)
            await asyncio.sleep(0.1)  # 전송 간격
```

---

### 에러 4: `TimeoutError` (카카오)

**원인:** GPT 응답이 5초 초과

**해결:**
```python
# app/main.py
answer_data = await asyncio.wait_for(
    generate_answer(question, results),
    timeout=3.0  # 3초로 단축 (여유 시간 확보)
)

# 또는 캐시 사용
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_search(query: str):
    return search_documents(query, k=5)
```

---

### 에러 5: Markdown 파싱 오류 (텔레그램)

**원인:** 특수문자 이스케이프 누락

**해결:**
```python
# app/formatters/telegram.py
def escape_markdown(text: str) -> str:
    # 모든 특수문자 이스케이프
    special = ["_", "*", "[", "]", "(", ")", "~", "`", ">", "#", "+", "-", "=", "|", "{", "}", ".", "!"]
    for char in special:
        text = text.replace(char, f"\\{char}")
    return text

# 사용
formatted = escape_markdown(answer_data["answer"])
```

---

## ✅ 단계별 체크리스트

### Week 2: 텔레그램 챗봇 (1일)

**Step 1-2: 봇 생성 & ngrok (30분)**
- [ ] BotFather에서 봇 생성 완료
- [ ] 봇 토큰 `.env`에 저장
- [ ] `/setprivacy` → Disable 설정
- [ ] ngrok 설치 및 터널 시작
- [ ] `TELEGRAM_WEBHOOK_URL` 확인

**Step 3: Webhook 구현 (2시간)**
- [ ] `app/clients/telegram.py` 작성
- [ ] `app/formatters/telegram.py` 작성
- [ ] `app/main.py`에 `/telegram/webhook` 추가
- [ ] Webhook 등록 (`setWebhook` API 호출)
- [ ] `getWebhookInfo`로 상태 확인

**Step 3-5: 테스트 (30분)**
- [ ] 텔레그램 앱에서 봇 검색
- [ ] 질문 3가지 입력 → 답변 확인
- [ ] 출처 표시 정상 작동
- [ ] Markdown 포맷 정상 (굵게, 기울임)
- [ ] 에러 처리 확인 (문서 없을 때)

---

### Week 2-3: 카카오톡 챗봇 (2일)

**Step 4-1: 채널 생성 (1시간)**
- [ ] 카카오 개발자 계정 생성
- [ ] 카카오톡 채널 생성/연결
- [ ] 오픈빌더 프로젝트 생성
- [ ] 시그니처 비밀키 복사 → `.env` 저장

**Step 4-2: 스킬 서버 구현 (3시간)**
- [ ] `app/security/kakao.py` 작성 (시그니처 검증)
- [ ] `app/formatters/kakao.py` 작성
- [ ] `app/main.py`에 `/kakao/router` 추가
- [ ] 시그니처 검증 테스트 (잘못된 요청 → 403)
- [ ] 타임아웃 처리 (3초 이내)

**Step 4-3: 검수 준비 (2시간)**
- [ ] 테스트 채널에서 10가지 질문 테스트
- [ ] 응답 시간 5초 이내 확인
- [ ] 에러 메시지 친절함 확인
- [ ] 출처 표시 정확함 확인
- [ ] 스크린샷 10장 촬영

---

### 최종 검증 (프리랜서 준비)

**기술 검증**
- [ ] 텔레그램/카카오 모두 정상 작동
- [ ] 시그니처 검증 정상 (해커 요청 차단)
- [ ] 타임아웃 처리 정상 (5초 초과 시 에러)
- [ ] 메시지 분할 정상 (4,096자 초과 시)

**데모 자료**
- [ ] 텔레그램 데모 영상 (1분)
- [ ] 카카오톡 데모 영상 (1분)
- [ ] 스크린샷 20장 (정상/에러/출처 표시)
- [ ] GitHub README에 챗봇 사용법 추가

**영업 준비**
- [ ] "멀티 채널 지원" 강조 (웹 + 텔레그램 + 카카오)
- [ ] 단가 상향 근거 작성 ("3채널 지원 = +600만원")
- [ ] FAQ 준비 ("모바일에서 바로 쓸 수 있나요?" → "네!")

---

## 🎓 다음 단계는?

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

## 📚 참고 자료

### 공식 문서
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [카카오 i 오픈빌더 문서](https://i.kakao.com)
- [ngrok 문서](https://ngrok.com/docs)

### 추천 학습
- [텔레그램 봇 만들기 (YouTube)](https://youtube.com) - "Telegram Bot Tutorial"
- [카카오 스킬 서버 가이드](https://i.kakao.com/docs/skill-response-format) - 응답 포맷 상세

### 문제 해결
- [`appendix/troubleshooting.md`](../appendix/troubleshooting.md) - "텔레그램 응답 실패", "카카오 403 에러"
- Stack Overflow #telegram-bot #kakao-i

---

## 🏆 마지막 당부

**초보자가 가장 많이 하는 실수:**

1. ❌ **ngrok URL을 하드코딩**
   - ✅ `.env`에 저장하고 환경변수로 읽기

2. ❌ **시그니처 검증 안 함**
   - ✅ 카카오는 필수! 검수 통과 안 됨

3. ❌ **타임아웃 처리 안 함**
   - ✅ 카카오는 5초 초과 시 실패 처리

4. ❌ **에러 메시지가 불친절**
   - ✅ "처리 중 오류가 발생했습니다. 잠시 후 다시 시도해 주세요."

5. ❌ **테스트 채널과 실서비스 채널 구분 안 함**
   - ✅ 테스트 완료 후 실서비스 채널로 전환

---

**🎉 텔레그램과 카카오톡 모두 연동했다면, 당신은 이미 고객이 원하는 것을 만들 수 있는 개발자입니다!**

다음 주차로 넘어가기 전에:
- [ ] 체크리스트 재확인
- [ ] 데모 영상 2개 촬영 (텔레그램 + 카카오)
- [ ] GitHub에 코드 푸시

**다음 단계:** [`implementation/web-admin.md`](web-admin.md)에서 웹 데모 UI를 만들어 봅시다! 🚀
