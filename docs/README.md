# RAG 포트폴리오 마스터 가이드

> **목표**: 8주 안에 텔레그램/웹/카카오 기반 RAG 챗봇 두 종류를 완성하고, 외주 수주에 필요한 산출물까지 준비한다.

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

| 문서                                                               | 샘플 코드                | 실습 스텝                                        |
| ------------------------------------------------------------------ | ------------------------ | ------------------------------------------------ |
| [`roadmap/week01-08.md`](roadmap/week01-08.md)                     | 주차별 체크리스트        | 주차별 목표 설정 → 산출물 업로드 → 리뷰          |
| [`implementation/rag-pipeline.md`](implementation/rag-pipeline.md) | 업로드→임베딩 파이프라인 | 문서 파싱 → 청크 분할 → 벡터 색인 → 응답 생성    |
| [`implementation/bots.md`](implementation/bots.md)                 | 텔레그램/카카오 웹훅     | BotFather/오픈빌더 설정 → Webhook 구현 → QA      |
| [`implementation/web-admin.md`](implementation/web-admin.md)       | 웹 데모 & 관리자 페이지  | index.html 작성 → Fetch API 연동 → 통계 API 구현 |
| [`business/package.md`](business/package.md)                       | 제안서/영업 템플릿       | 패키지 선택 → 온보딩 체크리스트 → 제안/계약 작성 |
| [`appendix/setup-requirements.md`](appendix/setup-requirements.md) | `requirements.txt`       | 가상환경 구성 → 패키지 설치 → `.env` 설정        |
| [`appendix/troubleshooting.md`](appendix/troubleshooting.md)       | -                        | 장애 대응 → FAQ → SLA 운영                       |

> 모든 문서는 **샘플 코드**와 **실습 스텝** 섹션을 포함합니다. 우선 코드를 돌려보고, 그다음 원리를 이해하는 방식으로 진행하세요.

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

1. `git clone` 후 가상환경 생성 → `pip install -r requirements.txt`
2. `.env.example`을 복사해 `.env` 작성 (`OPENAI_API_KEY` 포함)
3. `uvicorn app.main:app --reload` 로 기본 서버 실행
4. `roadmap/week01-08.md` Week 1 체크리스트를 노션에 복사
5. 샘플 문서 1개로 `/upload` → `/ask`까지 스모크 테스트

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

