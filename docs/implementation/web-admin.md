# 웹 데모 & 관리자/로그 기능 가이드

## 개요
이 문서는 **웹 클라이언트 데모**와 **관리자 페이지**(권한·로그·비용 모니터링) 구현 방법을 정리합니다. Week 3~6 로드맵에 해당하며, 고객사 데모 및 운영 신뢰도를 높이는 핵심 요소입니다.

---

## 1. 웹 데모 (Week 3)

### 1.1 구조
- `web/index.html`: 정적 HTML + JS (Fetch API)
- `/ask` 엔드포인트 호출 → JSON 응답 처리
- 구성 요소
  - 질문 입력 폼
  - 로딩 스피너
  - 응답 카드 (마크다운 or 단순 HTML)
  - 출처 리스트
  - 에러 토스트
- **폴더 구성 예시**
  ```
  web/
    index.html
    assets/
      styles.css
      app.js
  ```
  `app.js`에서 Fetch 요청 및 DOM 조작을 담당하고, `styles.css`로 최소한의 스타일을 정리합니다.

### 1.2 API 명세
- 요청
  ```json
  POST /ask
  Content-Type: application/json
  {
    "question": "사내 복지 포인트 잔액 확인 방법?"
  }
  ```
- 응답
  ```json
  {
    "answer": "사내 포털 > 인사정보... (중략)",
    "sources": [
      {"title": "복지 포털 가이드", "page": "p.5", "url": "https://..."},
      {"title": "FAQ 2024", "section": "2-1", "url": null}
    ],
    "token_usage": {"prompt": 850, "completion": 210},
    "cost": 0.0021
  }
  ```

### 1.3 UI 구현 팁
- Tailwind 또는 간단한 CSS 유틸을 사용해 빠르게 구성
- 로딩 상태 시 버튼 비활성화, 스피너 노출
- 출처는 카드 혹은 리스트(`title`, `page`, `url` 링크)
- 에러 메시지 예시:
  ```
  답변을 생성하지 못했습니다.
  잠시 후 다시 시도하거나 다른 질문을 입력해 주세요.
  ```
- GA/Amplitude 등 이벤트 추적(선택)
- **샘플 코드 조각**
  ```html
  <!-- index.html -->
  <form id="ask-form">
    <label>질문</label>
    <textarea id="question" required></textarea>
    <button type="submit">질문하기</button>
  </form>
  <div id="answer"></div>
  <ul id="sources"></ul>
  <div id="toast" class="hidden"></div>
  <script src="assets/app.js"></script>
  ```
  ```javascript
  // assets/app.js
  document.getElementById("ask-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const question = document.getElementById("question").value.trim();
    toggleLoading(true);
    try {
      const res = await fetch("/ask", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({question})
      });
      if (!res.ok) throw new Error("요청 실패");
      const data = await res.json();
      renderAnswer(data);
    } catch (err) {
      showToast("답변을 생성하지 못했습니다.");
      console.error(err);
    } finally {
      toggleLoading(false);
    }
  });
  ```

### 1.4 배포 전 체크
- [ ] 모바일 반응형 최소 대응
- [ ] API 401/403 시 로그인 페이지로 리다이렉트(Week 6 적용)
- [ ] 테스트 케이스(정상/에러/출처 없음) 캡처 저장
- **테스트 팁**
  - 크롬 DevTools → Lighthouse로 접근성/성능 점수 확인 후 개선
  - 질문 입력에 Enter 키로 제출되지 않도록 `Shift+Enter` 안내
  - `fetch` 타임아웃 대비 `AbortController` 사용 권장

---

## 2. 관리자 · 권한 기능 (Week 6)

### 2.1 사용자/권한 모델
- 테이블 예시 (`SQLite/Postgres`)
  - `users(id, email, password_hash, role, team)`
  - `documents(id, title, access_level, source_url, created_at)`
  - `document_access(document_id, role_or_team)`
- JWT 토큰 페이로드
  ```json
  {
    "sub": "user_id",
    "role": "manager",
    "team": "cs",
    "exp": 1710000000
  }
  ```

### 2.2 권한 필터링
- `retriever.search()` 호출 전, 사용자 정보 기반으로 `where` 조건 추가
- 예시:
  ```python
  filters = {"$or": [{"access_level": {"$in": ["public", user.role]}},
                     {"team": user.team}]}
  results = chroma.query(query_texts=[question], where=filters)
  ```
- 권한 불충분 시 “권한이 필요한 문서입니다” 안내

### 2.3 관리자 대시보드
- 라우트: `/admin` (로그인 필요)
- 핵심 위젯
  - 일별 요청 수 & 토큰 사용량 (Line chart)
  - 채널별 비율(텔레그램/웹/카카오)
  - 상위 질문 키워드 (Word cloud or 테이블)
  - 비용 추정(OpenAI 단가 기반)
- 라이브러리: `Chart.js`, `Plotly`, 혹은 `ECharts`
- 데이터 API
  - `/admin/stats/daily?from=...&to=...`
  - `/admin/stats/top-queries?limit=10`
  - `/admin/stats/cost?group_by=channel`

### 2.4 로깅 스키마
- `requests` 테이블
  | 필드 | 설명 |
  | --- | --- |
  | `id` | PK |
  | `user_id` | 사용자 FK (익명일 경우 null) |
  | `channel` | `web/telegram/kakao` |
  | `question` | 원문 |
  | `answer` | 요약본 또는 전문 |
  | `sources` | JSON 배열 |
  | `token_in` / `token_out` | LLM 토큰 수 |
  | `cost` | USD 또는 KRW |
  | `latency_ms` | 응답 시간 |
  | `created_at` | 타임스탬프 |

- 비용 계산 예시
  ```python
  cost = (token_in / 1000 * PROMPT_PRICE) + (token_out / 1000 * COMPLETION_PRICE)
  ```

### 2.5 감사/보안
- PII(개인정보) 로그 저장 금지 → 필요한 경우 마지막 4자리 마스킹
- 관리자 접근은 RBAC(Role Based Access Control) 적용
- `admin` 라우트에 rate-limit 및 IP 화이트리스트 옵션 고려
- **감사 로그 예시**
  ```json
  {
    "event": "admin_login",
    "user_id": "manager-01",
    "ip": "203.0.113.10",
    "result": "success",
    "created_at": "2025-11-22T10:42:00+09:00"
  }
  ```

---

## 3. 알림 & 모니터링
- 에러 발생 시 Slack/Email 알림 (`apscheduler` 혹은 `celery`)
- API `healthz`, `metrics` 엔드포인트 제공 → UptimeRobot/CloudWatch 연동
- 주간 리포트
  - 기본 템플릿: 주간 질문 수, 정확도, 비용, 개선 요청
  - PDF or 노션 자동 업데이트 (Zapier, Make)

---

## 다음 단계
- 챗봇 연동은 [`implementation/bots.md`](bots.md)를 참고하세요.
- 영업 자료 제작은 [`business/package.md`](../business/package.md)에서 이어집니다.

