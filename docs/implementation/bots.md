# 챗봇 연동 가이드 (텔레그램 · 카카오)

> **목표**: 동일한 RAG 파이프라인을 활용해 텔레그램과 카카오 i 오픈빌더 채널을 모두 지원한다.

---

## 🎯 학습 목표

| Step | 결과                    | 핵심 역량                                  |
| ---- | ----------------------- | ------------------------------------------ |
| 1    | 텔레그램 봇 웹훅 구성   | BotFather 설정, HTTPS Webhook, 메시지 포맷 |
| 2    | 카카오 스킬 서버 연동   | 시그니처 검증, JSON 변환, 타임아웃 대응    |
| 3    | 공통 서비스 레이어 설계 | 채널별 포맷터, `rag_service` 재사용        |
| 4    | 운영/보안 체크          | Rate limit, 금칙어, 로그/비용 모니터링     |

---

## 🛠️ 준비물

| 항목     | 상세                                                                                             |
| -------- | ------------------------------------------------------------------------------------------------ |
| 텔레그램 | BotFather 계정, 봇 토큰, HTTPS 도메인(ngrok 등)                                                  |
| 카카오   | 카카오톡 채널, 오픈빌더 프로젝트, 시그니처 비밀키                                                |
| 환경변수 | `.env`에 `TELEGRAM_BOT_TOKEN`, `TELEGRAM_WEBHOOK_URL`, `KAKAO_CHANNEL_SECRET`, `KAKAO_SKILL_URL` |
| 네트워크 | 200ms 이상 응답 지연 시 대비(타임아웃, 재시도)                                                   |

---

## 💻 샘플 코드 시작점

```python
# app/main.py
from fastapi import FastAPI, Request, HTTPException
from app.services import rag_service
from app.clients.telegram import send_message
from app.clients.kakao import send_skill_response
from app.security import verify_kakao_signature

app = FastAPI()

@app.post("/telegram/webhook")
async def telegram_webhook(update: dict):
    message = update.get("message") or {}
    chat_id = message.get("chat", {}).get("id")
    text = message.get("text", "")
    response = await rag_service.ask(text, channel="telegram")
    await send_message(chat_id=chat_id, text=response.render_markdown())
    return {"ok": True}


@app.post("/kakao/router")
async def kakao_router(request: Request):
    body = await request.body()
    signature = request.headers.get("X-Kakao-Signature")
    if not verify_kakao_signature(body, signature):
        raise HTTPException(status_code=403, detail="invalid signature")
    payload = await request.json()
    question = payload["userRequest"]["utterance"]
    response = await rag_service.ask(question, channel="kakao")
    return send_skill_response(response)
```

---

## 🔄 단계별 실습 가이드

### 1. 텔레그램 Webhook 연결

1. **BotFather 설정**
   - `/newbot` → 토큰 발급
   - `/setprivacy` → “Disable” (모든 메시지 수신)
2. **Webhook 등록**
   ```bash
   curl -X POST https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/setWebhook \
     -H "Content-Type: application/json" \
     -d "{\"url\": \"$TELEGRAM_WEBHOOK_URL\"}"
   ```
3. **메시지 처리 규칙**
   - Markdown 포맷 사용 시 `_` 문자 이스케이프
   - 4096자 초과 시 메시지 분할 전송
4. **테스트 체크리스트**
   - [ ] 문서 기반 질문 3건 (정상/부분/없는 내용)
   - [ ] 금칙어 필터 → 운영자 안내
   - [ ] 5회 연속 질문 → Rate-limit 응답

### 2. 카카오 i 오픈빌더 연동

1. **스킬 서버 등록**
   - 오픈빌더 → 스킬 → 스킬 서버 URL 입력 (`https://.../kakao/router`)
   - 시그니처 비밀키 복사 → `.env` 저장
2. **시그니처 검증**
   ```python
   import base64, hashlib, hmac

   def verify_kakao_signature(body: bytes, signature: str) -> bool:
       mac = hmac.new(settings.kakao_secret.encode(), body, hashlib.sha256)
       digest = base64.b64encode(mac.digest()).decode()
       return hmac.compare_digest(digest, signature)
   ```
3. **응답 포맷**
   ```python
   def to_skill_response(answer: str, sources: list[dict]) -> dict:
       source_text = "\n".join(
           f"- {src['title']} p.{src.get('page','?')}" for src in sources
       ) or "- 출처 없음"
       return {
           "version": "2.0",
           "template": {
               "outputs": [
                   {
                       "simpleText": {
                           "text": f"{answer}\n\n출처:\n{source_text}"
                       }
                   }
               ]
           }
       }
   ```
4. **검수 포인트**
   - 5초 안에 응답 (LLM 타임아웃 3초 설정)
   - fallback 블록 구성 (오류 시 안내 문구)
   - 테스트 채널과 실 서비스 채널 분리 관리

### 3. 공통 서비스/포맷터 설계

```
app/
  services/
    rag_service.py   # channel별 정책 분기
  clients/
    telegram.py      # send_message, typing indicator
    kakao.py         # send_skill_response
  formatters/
    telegram.py      # Markdown escape
    kakao.py         # simpleText/basicCard 생성
```

- `rag_service.ask(question, channel)`에서 채널별 포맷 옵션 적용
- 로깅 시 `channel` 필드 포함 → 비용/사용량 집계
- Rate-limit → IP or user id 기준 (`30 req/min` 예시)

---

## ✅ 체크리스트

- [ ] `.env`에 텔레그램/카카오 환경변수가 설정되어 있다.
- [ ] `/telegram/webhook`에서 업데이트 로그가 수신된다.
- [ ] `/kakao/router` 시그니처 검증 실패 시 403을 반환한다.
- [ ] `rag_service`가 채널별 포맷터와 로깅을 지원한다.
- [ ] 정상/헛소리/금칙어/오류 시나리오 테스트 결과를 노션에 기록했다.

---

## 🧪 QA & 모니터링

| 항목        | 텔레그램                          | 카카오                                  |
| ----------- | --------------------------------- | --------------------------------------- |
| 상태 확인   | `getWebhookInfo`                  | 오픈빌더 로그                           |
| 재시도 전략 | `sendChatAction`으로 typing 표시  | “처리 중입니다” simpleText 후 후속 응답 |
| 장애 대응   | 폴링 모드 fallback (`getUpdates`) | 테스트 채널 유지, 재검수 대비           |

- 에러 발생 시 Slack/Email 알림 → [`appendix/troubleshooting.md`](../appendix/troubleshooting.md) 참고
- 주 1회 토큰 사용량/비용 리포트 공유

---

## 📚 참고 & 다음 학습

- [Telegram Bot API](https://core.telegram.org/bots/api)
- [카카오 i 오픈빌더 문서](https://i.kakao.com)
- 배포/로그 모니터링 강화는 [`implementation/web-admin.md`](web-admin.md)로 이동
- 정확도 개선은 `Week 4` 로드맵과 [`implementation/rag-pipeline.md`](rag-pipeline.md)에서 이어서 진행

채널 운영 중 문제가 발생하면 `appendix/troubleshooting.md`의 “텔레그램 응답 실패”, “카카오 403 에러” 섹션을 먼저 확인하세요.

