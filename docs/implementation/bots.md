# 챗봇 연동 가이드 (텔레그램·카카오)

## 개요
이 문서는 FastAPI 기반 RAG 백엔드에 **텔레그램 봇**과 **카카오 i 오픈빌더**를 연결하는 과정을 단계별로 안내합니다. 공통 파이프라인을 재사용하면서 보안 검증, 에러 처리, 운영 체크리스트까지 포함합니다.

---

## 1. 텔레그램 봇 연동

### 1.1 사전 준비
1. **BotFather**에게 `/newbot` 전송 → 봇 이름, 사용자명 설정
2. 발급받은 토큰을 `.env`에 저장
   ```
   TELEGRAM_BOT_TOKEN=123456:ABC-...
   TELEGRAM_WEBHOOK_URL=https://your-domain.com/telegram/webhook
   ```
3. 서버에 HTTPS 도메인 준비 (ngrok 임시 사용 가능)

### 1.2 FastAPI 라우트 구현
- `app/main.py` 혹은 `app/routers/telegram.py`에 다음 로직을 구성
  - `POST /telegram/webhook`: 텔레그램 업데이트 수신
  - 메시지 텍스트 추출 후 `RAGService.ask()` 호출
  - 답변과 출처를 포맷 → `sendMessage` API 호출
- 템플릿 코드 스니펫
  - `telegram_client`는 `httpx.AsyncClient`를 래핑해 재사용

```startLine:endLine:app/main.py
# ... existing code ...
@app.post("/telegram/webhook")
async def telegram_webhook(update: dict):
    message = update.get("message") or {}
    chat_id = message.get("chat", {}).get("id")
    text = message.get("text", "")
    response = rag_service.ask(text, channel="telegram")
    payload = {
        "chat_id": chat_id,
        "text": format_telegram_response(response),
        "parse_mode": "Markdown",
    }
    await telegram_client.send(payload)
    return {"ok": True}
# ... existing code ...
```

### 1.3 Webhook 등록
```bash
curl -X POST https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/setWebhook \
  -H "Content-Type: application/json" \
  -d "{\"url\": \"$TELEGRAM_WEBHOOK_URL\"}"
```

### 1.4 메시지 포맷 가이드
- 답변 본문 + 출처 목록
  ```
  답변 내용

  출처:
  • 문서명 | p.12 | https://...
  • 문서명 | 섹션 3 | 내부 링크
  ```
- 임계치 미달 시:
  ```
  자료에서 근거를 찾지 못했습니다.
  관련 문서를 업로드해 주시면 더 정확히 답변드릴게요!
  ```

### 1.5 운영 체크리스트
- 메시지 길이 4096자 제한 → 긴 답변은 2개 메시지로 분할
- 봇 다운 대비 `/healthz` 엔드포인트 모니터링
- 로그에 사용자 ID 저장 시 개인정보 보호 가이드 준수
- **테스트 시나리오**
  1. 문서에 있는 질문 → 정상 답변과 출처 확인
  2. 문서에 없는 질문 → “근거 없음” 안내 메시지 확인
  3. 금칙어(예: 욕설) → 필터링 후 운영자 연결 안내
  4. 연속 질문(5회 이상) → Rate-limit 로직 정상 동작 여부 확인
- **문제 해결**
  - 응답이 늦다면 `asyncio.create_task`로 LLM 호출 후 typing indicator 전송
  - Webhook 업데이트 실패는 `ngrok logs` 혹은 텔레그램 `getWebhookInfo`에서 오류 메시지를 확인

---

## 2. 카카오 i 오픈빌더 연동

### 2.1 사전 준비
1. 카카오톡 채널 생성 → 오픈빌더 프로젝트 생성
2. `스킬` > `스킬 서버`에 HTTPS URL 등록
3. 환경변수 설정
   ```
   KAKAO_CHANNEL_SECRET=your_secret
   KAKAO_SKILL_URL=https://your-domain.com/kakao/router
   ```

### 2.2 시그니처 검증
- 카카오 요청 헤더 `X-Kakao-Signature` 검증 필수
- 예시:

```startLine:endLine:bots/kakao_router.py
# ... existing code ...
def verify_signature(body: bytes, signature: str) -> bool:
    mac = hmac.new(settings.kakao_secret.encode(), body, hashlib.sha256)
    digest = base64.b64encode(mac.digest()).decode()
    return hmac.compare_digest(digest, signature)
# ... existing code ...
```

### 2.3 요청/응답 포맷 변환
- 카카오 스킬 서버 요청 구조
  ```json
  {
    "userRequest": {
      "utterance": "문의 내용",
      "user": {"id": "abc123", "properties": {"plusfriendUserKey": "..."}}
    },
    "bot": {...},
    "action": {...}
  }
  ```
- 응답 예시
  ```json
  {
    "version": "2.0",
    "template": {
      "outputs": [
        {"simpleText": {"text": "답변 내용\n\n출처:\n- ..."}}
      ]
    }
  }
  ```
- `bots/kakao_router.py`에서 변환 레이어 작성:
  - 요청 파싱 → `rag_service.ask(question, channel="kakao")`
  - 출처를 문자열로 조합하여 `simpleText` 또는 `basicCard` 활용

### 2.4 에러 처리
- 시그니처 실패: `403 Forbidden`
- 내부 오류: `500` 반환 + 슬랙/이메일 알림
- 사용자 입력 미존재: 가이드 메시지 반환
- **테스트 체크리스트**
  - 시그니처를 고의로 틀려 POST → 403 응답 확인
  - JSON 필드 일부 누락 시에도 graceful 한 예외 처리
  - LLM 타임아웃 발생 시 fallback 메시지 전송 후 로그 기록
- **운영 팁**
  - 오픈빌더 “테스트 채널”과 실서비스 채널은 별도로 존재 → 배포 전 테스트 채널에서 모든 시나리오 검증
  - 카카오 서버는 5초 이상 응답이 지연되면 타임아웃 → LLM 호출은 3초 이내 타임아웃을 설정하고, 지연 시 “처리 중” 메시지를 반환

### 2.5 QA 체크리스트
- [ ] 테스트 채널에서 5개 질문 성공
- [ ] 출처 목록 줄바꿈 정상
- [ ] fallback 블록 설정(비정상 응답 시 안내 메시지)
- [ ] 주기적 토큰 비용 리포트 공유

---

## 3. 공통 모듈화 전략
- 프로젝트 구조 예시
  ```
  app/
    services/rag_service.py
    clients/telegram.py
    clients/kakao.py
    formatters/telegram.py
    formatters/kakao.py
  ```
- `services/rag_service.py` 등 공통 서비스 레이어를 만들어 각 채널에서 재사용
- 채널별 포맷터 분리
  - 텔레그램: Markdown
  - 카카오: Plain text + 목록
- 로깅 시 `channel` 필드로 구분 → 분석/과금에 활용
- 요청 rate-limit: IP 혹은 user id 기준(예: 30 req/min)
- **테스트 전략**
  - 채널별 단위 테스트: 업데이트 JSON fixture → 응답 포맷 검증
  - 통합 테스트: `TestClient`로 `/telegram/webhook` 호출 후 LLM mock하여 빠른 응답 확인

## 4. 배포 & 운영 팁
- HTTPS 인증서는 Let’s Encrypt 자동 갱신 스크립트 구성
- 장애 대비: `status` 엔드포인트 제공 + 클라우드 모니터링(CloudWatch 등)
- 주기적 로그 검토로 금칙어 및 민감 발화 탐지
- 텔레그램은 `getUpdates` 폴링 테스트를 유지하면서, 장애 시 임시로 폴링 모드로 전환할 수 있도록 백업 플랜을 준비하세요.
- 카카오는 검수 기간(통상 1~3일)을 고려해 일정에 버퍼를 둡니다. 검수 시 요구하는 테스트 계정 정보도 미리 준비합니다.

## 다음 단계
- 웹 UI 및 관리자 기능은 [`implementation/web-admin.md`](web-admin.md)를 참고하세요.
- 정확도/가드레일 튜닝은 Week 4 로드맵과 연계하여 진행합니다.

