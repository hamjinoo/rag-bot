# RAG 포트폴리오 마스터 가이드

## 개요
이 문서 세트는 8주 안에 수익화 가능한 **RAG 기반 챗봇 포트폴리오 2종**(텔레그램/웹, 카카오/관리자)을 완성하기 위한 실전 가이드입니다. 기술 구현뿐 아니라 데모 제작, 영업 자료, 수주 전략까지 모두 포함합니다.

## 시작 전 준비물
- Python 3.10 이상, Git, Docker(Week 7용) 설치
- OpenAI API 키, 텔레그램 BotFather 계정, 카카오 i 오픈빌더 계정 준비
- VS Code 또는 PyCharm 등 IDE, ngrok/Cloudflare Tunnel(임시 HTTPS) 설치
- Windows 사용자는 `PowerShell` 대신 `cmd.exe` 또는 WSL 둘 중 하나를 기준으로 진행

## 문서 활용법
1. `roadmap/week01-08.md`에서 전체 일정을 훑어보고, 주차별 목표를 노션/캘린더에 옮겨 적습니다.
2. 각 주차에 해당하는 구현 문서를 차례대로 학습하며 실제 코드를 작성합니다.
3. 진행 중 막히는 부분은 `appendix/troubleshooting.md`에서 해결책을 찾고, 해결 후에는 노션 작업일지에 기록합니다.
4. Week 7 이후에는 `business/package.md`를 따라 영업 자료와 템플릿을 정리합니다.

## 문서 네비게이션
- [주차별 로드맵](roadmap/week01-08.md)
- 구현 가이드
  - [RAG 파이프라인](implementation/rag-pipeline.md)
  - [챗봇 연결(텔레그램·카카오)](implementation/bots.md)
  - [웹 UI·관리자/로그 기능](implementation/web-admin.md)
- 비즈니스 자산
  - [상품 패키지·영업 템플릿](business/package.md)
- 부록
  - [requirements.txt 작성 및 사용 가이드](appendix/setup-requirements.md)
  - [트러블슈팅·FAQ](appendix/troubleshooting.md)

## 바로 시작하기 체크리스트
1. [`appendix/setup-requirements.md`](appendix/setup-requirements.md)를 참고해 `requirements.txt` 기반 가상환경 생성 및 패키지 설치
2. [`implementation/rag-pipeline.md`](implementation/rag-pipeline.md)의 업로드→임베딩→검색→응답 플로우 구축
3. [`implementation/bots.md`](implementation/bots.md) 절차대로 텔레그램 챗봇 웹훅 연동
4. [`implementation/web-admin.md`](implementation/web-admin.md) 를 참고해 웹 데모 및 로그 스키마 추가
5. 완료 후 [`business/package.md`](business/package.md) 템플릿으로 제안서/가격표 준비

> **Tip**: 각 단계를 완료할 때마다 `docs/roadmap/week01-08.md` 의 완료 기준을 체크하고, 실제 산출물(코드/영상/스크린샷)을 노션 페이지에 링크로 정리해 둡니다.

## 주차별 목표 스냅샷
- **Week 1**: FastAPI + Chroma 기반 RAG 골격, 출처 포함 응답
- **Week 2**: 텔레그램 봇 연동 및 데모 영상
- **Week 3**: 웹 UI 완성, 스크린샷 확보
- **Week 4**: 정확도 평가/가드레일, 보고서 작성
- **Week 5-6**: 카카오 챗봇, 권한/로그/비용 모니터링
- **Week 7**: Docker·배포·운영 문서
- **Week 8**: 노션 소개 페이지, 가격·계약 패키지

## 산출물 체크
| 구분 | 필수 산출물                             | 비고                             |
| ---- | --------------------------------------- | -------------------------------- |
| 데모 | 텔레그램 영상, 웹 스크린샷, 카카오 영상 | 유튜브 비공개 링크/이미지        |
| 코드 | `rag-bot` GitHub 리포지토리             | README + `.env.example` + Docker |
| 분석 | 정확도 평가 리포트, 로그/비용 요약      | Week 4, Week 6 산출물 + 그래프   |
| 영업 | 노션 소개, 가격표, 제안/계약 템플릿     | Week 8에서 완성, PDF 백업 포함   |

## 다음 단계
- 처음이라면 [주차별 로드맵](roadmap/week01-08.md)을 따라가며 전체 흐름을 파악하세요.
- 구현 중 막히면 [트러블슈팅](appendix/troubleshooting.md)을 우선 확인하고, 필요 시 TODO를 갱신하며 진행합니다.

---

## 추천 작업 루틴
- **월/수/금 저녁 (1.5h)**: 구현 문서 학습 + 코드 작성
- **화/목 (1h)**: 테스트 및 데모 영상/스크린샷 정리
- **주말(4h)**: 정확도 튜닝, 관리자/배포 작업, 노션 문서 업데이트

## 진행 현황 기록 예시
| 날짜  | 한 일                             | 산출물 링크            | 다음 할 일         |
| ----- | --------------------------------- | ---------------------- | ------------------ |
| 11/10 | FastAPI 기본 엔드포인트 구현      | GitHub commit `abc123` | Chroma 색인 테스트 |
| 11/12 | 텔레그램 Webhook 연동, 테스트 5건 | Demo 영상(비공개)      | 웹 UI 초안 작성    |

> 위 표처럼 노션 혹은 스프레드시트에 매일 기록하면 8주 완료 시 포트폴리오 설명 자료로 바로 활용 가능합니다.

