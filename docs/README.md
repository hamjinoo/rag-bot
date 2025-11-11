# RAG 포트폴리오 마스터 가이드

> **목표**: 8주 안에 텔레그램/웹/카카오 기반 RAG 챗봇 두 종류를 완성하고, 외주 수주에 필요한 산출물까지 준비한다.
> 
> **이 문서의 특징**: 초보자도 혼자서 따라하며 프리랜서로 외주를 받을 수 있는 실력을 키울 수 있도록, **"왜 배우나?" → "개념 이해" → "따라하기" → "에러 해결"**까지 단계별로 상세히 설명합니다.

---

## 🎯 이 가이드를 따라하면?

**Before (일반 개발자)**
```
고객: "우리 회사 규정집 챗봇 만들어주세요."
개발자: "ChatGPT API 연결해드릴게요."
고객: "그럼 어떻게 우리 문서를 학습시키나요?"
개발자: "...?" 💥
```

**After (이 가이드 완료 후)**
```
고객: "우리 회사 규정집 챗봇 만들어주세요."
여러분: "PDF 업로드하시면 자동으로 색인됩니다.
       출처도 표시되고, 권한별로 접근 제어도 가능합니다.
       텔레그램과 카카오톡 모두 지원합니다. 데모 보여드릴까요?" ✨
고객: "오, 바로 쓸 수 있네요! 계약 진행하겠습니다."
```

**예상 외주 단가:**
- 기본 (웹만): 800만원
- 표준 (웹 + 챗봇): 1,200만원
- 고급 (웹 + 챗봇 + 관리자): 1,800~2,000만원

---

## 📦 무엇을 배우나요?

| 구분          | 결과물                                            | 핵심 역량                          |
| ------------- | ------------------------------------------------- | ---------------------------------- |
| **기술**      | 문서 업로드 → 임베딩 → 검색 → GPT 응답 파이프라인 | FastAPI, LangChain, Chroma, OpenAI |
| **운영**      | 권한/로그/비용 모니터링, 관리자 대시보드          | JWT, SQLAlchemy, 차트/리포트       |
| **채널 연동** | 텔레그램 & 카카오 챗봇                            | Webhook, 시그니처 검증, 응답 포맷  |
| **비즈니스**  | 노션 소개, 가격표, 제안서·계약서                  | 영업 스크립트, 견적 프로세스       |

---

## 🧭 학습 지도

| 문서                                                               | 핵심 내용                                                             | 학습 시간 | 난이도 |
| ------------------------------------------------------------------ | --------------------------------------------------------------------- | --------- | ------ |
| [`roadmap/week01-08.md`](roadmap/week01-08.md)                     | 주차별 체크리스트, 목표 설정, 산출물 관리                             | 참고용    | ⭐      |
| [`implementation/rag-pipeline.md`](implementation/rag-pipeline.md) | **Step 1**: RAG 파이프라인 (왜 배우나? → 개념 → 따라하기 → 에러 해결) | Week 1    | ⭐⭐     |
| [`implementation/bots.md`](implementation/bots.md)                 | **Step 2**: 텔레그램/카카오 챗봇 (Webhook, 시그니처 검증, 검수 준비)  | Week 2    | ⭐⭐     |
| [`implementation/web-admin.md`](implementation/web-admin.md)       | **Step 3**: 웹 데모 & 관리자 페이지 (HTML+JS, JWT, 통계 차트)         | Week 3~6  | ⭐⭐⭐    |
| [`business/package.md`](business/package.md)                       | 제안서/영업 템플릿, 단가 협상 가이드, 계약서 작성                     | Week 8    | ⭐      |
| [`appendix/setup-requirements.md`](appendix/setup-requirements.md) | `requirements.txt` 작성법, 가상환경 구성, `.env` 설정                 | Day 1     | ⭐      |
| [`appendix/troubleshooting.md`](appendix/troubleshooting.md)       | 자주 만나는 에러와 해결법, FAQ, 장애 대응                             | 참고용    | ⭐      |

### 📚 각 문서의 특징

**모든 구현 문서(`implementation/*.md`)는 다음 구조를 포함합니다:**

1. **🎯 이 단계를 배우는 이유** - 왜 필요한가? (실무 가치, 외주 단가)
2. **💡 핵심 개념 먼저 이해하기** - 원리부터 설명 (비유와 예시)
3. **🔄 따라하기 - 처음부터 끝까지** - Step 1~8 상세 명령어
4. **❌ 자주 만나는 에러와 해결법** - 5가지 이상의 에러 + 해결책
5. **✅ 단계별 체크리스트** - Week별 세밀한 검증 포인트
6. **💼 프리랜서 생존 팁** - 제안서 작성, 단가 협상 가이드

> **학습 방법**: 우선 코드를 돌려보고, 그다음 원리를 이해하는 방식으로 진행하세요. 각 Step마다 테스트 파일을 실행해 검증하면서 진행하면 실수를 줄일 수 있습니다.

---

## 🛠️ 시작 전 체크리스트

- [ ] Python 3.10+, Git, Docker 설치 (Windows는 `cmd.exe` 또는 WSL 사용 권장)
- [ ] OpenAI API 키, 텔레그램 BotFather 토큰, 카카오 i 오픈빌더 계정 준비
- [ ] VS Code / PyCharm + Thunder Client 또는 Insomnia 설치
- [ ] ngrok / Cloudflare Tunnel 등 HTTPS 터널 도구 설치
- [ ] 노션 또는 스프레드시트에 작업 일지 템플릿 생성

참고 문서: [`appendix/setup-requirements.md`](appendix/setup-requirements.md)

---

## 🚀 바로 실행하기 (Day 1)

### 추천 학습 순서

**1단계: 환경 설정 (30분)**
- [`appendix/setup-requirements.md`](appendix/setup-requirements.md) 따라하기
- 가상환경 생성 → `pip install -r requirements.txt`
- `.env.example`을 복사해 `.env` 작성 (`OPENAI_API_KEY` 포함)

**2단계: RAG 파이프라인 구축 (Week 1, 4~6시간)**
- [`implementation/rag-pipeline.md`](implementation/rag-pipeline.md) Step 1~8 따라하기
- 폴더 구조 생성 → PDF 파서 → 청크 분할 → 벡터 색인 → GPT 응답
- 각 Step마다 테스트 파일 실행해 검증

**3단계: 챗봇 연동 (Week 2, 2~3일)**
- [`implementation/bots.md`](implementation/bots.md) 따라하기
- 텔레그램 먼저 (쉬움) → 카카오톡 나중에 (검수 필요)

**4단계: 웹 데모 & 관리자 (Week 3~6)**
- [`implementation/web-admin.md`](implementation/web-admin.md) 따라하기
- 웹 데모 먼저 (1일) → 관리자 페이지 나중에 (Week 6)

### 빠른 스모크 테스트

```bash
# 1. 서버 실행
uvicorn app.main:app --reload

# 2. 브라우저에서 확인
# http://localhost:8000 → {"status": "ok"}
# http://localhost:8000/docs → Swagger UI

# 3. 샘플 문서 1개로 테스트
# (rag-pipeline.md Step 4~6 완료 후)
python tests/test_full_pipeline.py
```

---

## 📅 8주 스냅샷

| 주차   | 주요 목표           | 산출물                          |
| ------ | ------------------- | ------------------------------- |
| Week 1 | RAG 파이프라인 골격 | FastAPI 엔드포인트, Chroma 색인 |
| Week 2 | 텔레그램 챗봇       | Webhook 구현, 데모 영상         |
| Week 3 | 웹 데모 UI          | 스크린샷, 로딩/에러 처리        |
| Week 4 | 정확도 & 가드레일   | 평가 리포트, 가드레일 정책      |
| Week 5 | 카카오 챗봇         | 오픈빌더 연동, 시그니처 검증    |
| Week 6 | 권한·로그·비용      | 관리자 캡처, 로그 스키마        |
| Week 7 | 배포 & 운영         | Dockerfile, 배포 URL            |
| Week 8 | 영업 자산           | 노션 소개, 가격/계약 템플릿     |

상세 실습은 [`roadmap/week01-08.md`](roadmap/week01-08.md)를 참고하세요.

---

## 📋 산출물 점검표

| 카테고리 | 필수 산출물                             | 제출 방식                        |
| -------- | --------------------------------------- | -------------------------------- |
| 데모     | 텔레그램 영상, 웹 스크린샷, 카카오 영상 | 유튜브 비공개 링크 & 이미지      |
| 코드     | `rag-bot` GitHub 리포지토리             | README + `.env.example` + Docker |
| 품질     | 정확도 리포트, 로그/비용 요약           | Week 4 & 6 리포트, 그래프 포함   |
| 영업     | 노션 소개, 가격표, 제안/계약 템플릿     | 노션 공유 링크 + PDF 백업        |

> 각 산출물은 노션 작업일지와 GitHub Releases에 함께 기록해 두면 실제 외주 제안 시 증빙 자료로 활용하기 좋습니다.

---

## 🧪 셀프 체크 & 루틴

- **Daily**: 작업 후 `git status` + 노션 작업일지 업데이트
- **Weekly**: 산출물 캡처/영상 정리, 정확도·비용 지표 리뷰
- **Milestone 리뷰**: Week 4, Week 6, Week 8 완료 시 회고 → README에 변경사항 반영

작업 기록 예시:

| 날짜  | 작업 내용                      | 산출물              | 다음 액션          |
| ----- | ------------------------------ | ------------------- | ------------------ |
| 11/10 | FastAPI `/upload`, `/ask` 초안 | commit `abc123`     | Chroma 색인 테스트 |
| 11/12 | 텔레그램 Webhook + 영상 촬영   | YouTube 비공개 링크 | 웹 UI 초안         |

---

## 🔗 확장 학습 (Spring Boot)

RAG 챗봇과 별도로 백엔드 역량을 확장하고 싶다면 아래 문서를 참고하세요.

| 문서                                                                                    | 내용                                 |
| --------------------------------------------------------------------------------------- | ------------------------------------ |
| [`Step_01_스프링부트_기초.md`](../docs2/Step_01_스프링부트_기초.md)                     | 스프링부트 기본 개념 및 첫 API       |
| [`Step_02_기본_게시판_API.md`](../docs2/Step_02_기본_게시판_API.md)                     | 게시판 CRUD, Service/Repository 구조 |
| [`README_마이크로서비스_학습_로드맵.md`](../docs2/README_마이크로서비스_학습_로드맵.md) | 마이크로서비스 전환 로드맵           |

---

## 🆘 막히면 이렇게

1. [`appendix/troubleshooting.md`](appendix/troubleshooting.md)에서 오류 유형을 찾는다.
2. 해결이 안 되면 로그/스크린샷을 노션에 기록하고 다음 날 30분 “버그 처리 시간”을 확보한다.
3. 반복적으로 발생하는 이슈는 README FAQ 섹션에 추가한다.

---

## ✅ 다음 단계

1. `roadmap/week01-08.md` Week 1 항목을 시작한다.
2. 첫 산출물(코드/영상)을 노션과 GitHub에 기록한다.
3. 스프린트 종료 시 README에 “진행 상황 요약”을 추가해 두자.

성공적인 포트폴리오 완성을 응원합니다! 🚀

