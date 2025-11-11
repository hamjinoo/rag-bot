# requirements.txt 작성 및 사용 가이드

## 개요
이 문서는 RAG 봇 프로젝트에 필요한 Python 패키지들을 `requirements.txt`에 정리하고, 가상환경에서 설치 및 관리하는 방법을 설명합니다.

## requirements.txt 구조

### 기본 패키지 (Week 1-3)
```txt
# 웹 프레임워크
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6

# 환경변수 관리
python-dotenv==1.0.0

# RAG 파이프라인
langchain==0.1.0
langchain-openai==0.0.2
langchain-community==0.0.10
chromadb==0.4.18

# 문서 파싱
pypdf==3.17.1
python-docx==1.1.0
pandas==2.1.3

# HTTP 클라이언트
httpx==0.25.1
requests==2.31.0

# 유틸리티
pydantic==2.5.0
pydantic-settings==2.1.0
tiktoken==0.5.1
```

### 추가 패키지 (Week 4-6)
```txt
# 데이터베이스 (Week 6)
sqlalchemy==2.0.23
alembic==1.12.1

# 인증 (Week 6)
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4

# 테스트
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
```

### 선택적 패키지 (고급 기능)
```txt
# 로컬 임베딩 모델 (비용 절감용)
sentence-transformers==2.2.2

# 모니터링
sentry-sdk==1.38.0

# 차트 라이브러리 (관리자 페이지용)
plotly==5.18.0
```

## 패키지 설명

### 필수 패키지

#### FastAPI 관련
- **fastapi**: REST API 프레임워크
- **uvicorn**: ASGI 서버 (FastAPI 실행)
- **python-multipart**: 파일 업로드 지원

#### RAG 파이프라인
- **langchain**: RAG 파이프라인 구축 라이브러리
- **langchain-openai**: OpenAI 모델 연동
- **langchain-community**: 커뮤니티 확장 기능
- **chromadb**: 벡터 데이터베이스 (로컬)

#### 문서 파싱
- **pypdf**: PDF 파일 텍스트 추출
- **python-docx**: Word 문서 텍스트 추출
- **pandas**: CSV 파일 처리

#### 유틸리티
- **python-dotenv**: `.env` 파일에서 환경변수 로드
- **pydantic**: 데이터 검증 및 설정 관리
- **tiktoken**: OpenAI 토큰 수 계산
- **httpx**: 비동기 HTTP 클라이언트 (텔레그램/카카오 API 호출)

### 선택적 패키지

#### 데이터베이스 (Week 6)
- **sqlalchemy**: ORM (PostgreSQL/SQLite)
- **alembic**: 데이터베이스 마이그레이션

#### 인증 (Week 6)
- **python-jose**: JWT 토큰 생성/검증
- **passlib**: 비밀번호 해싱

#### 테스트
- **pytest**: 테스트 프레임워크
- **pytest-asyncio**: 비동기 테스트 지원
- **pytest-cov**: 코드 커버리지 측정

## 설치 방법

### 1. 가상환경 생성

#### Windows (cmd.exe)
```bash
python -m venv .venv
.venv\Scripts\activate
```

#### Windows (PowerShell)
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

> **PowerShell 실행 정책 오류 시**: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` 실행 후 재시도

#### Linux/macOS
```bash
python -m venv .venv
source .venv/bin/activate
```

### 2. 패키지 설치

#### 기본 패키지 설치
```bash
pip install -r requirements.txt
```

#### 업그레이드 (최신 버전으로)
```bash
pip install --upgrade -r requirements.txt
```

#### 특정 패키지만 설치
```bash
pip install fastapi uvicorn
```

### 3. 설치 확인
```bash
pip list
```

또는 특정 패키지 버전 확인:
```bash
pip show fastapi
```

### 4. 환경변수 설정
패키지 설치가 완료되면 `.env` 파일을 생성해야 합니다:

```bash
# .env.example 파일을 복사하여 .env 생성
copy .env.example .env  # Windows
cp .env.example .env    # Linux/macOS
```

그 다음 `.env` 파일을 열어 필요한 값(예: `OPENAI_API_KEY`)을 입력하세요.
> **참고**: `.env.example` 파일에는 모든 환경변수 예시가 포함되어 있습니다. 프로젝트 루트 디렉터리에 `.env` 파일을 만들어 실제 값을 입력하세요.

## 패키지 관리 팁

### 버전 고정
- `requirements.txt`에 버전을 명시하면 동일한 환경을 재현할 수 있습니다.
- 예: `fastapi==0.104.1` (정확한 버전), `fastapi>=0.104.1` (최소 버전)

### requirements.txt 업데이트
현재 설치된 패키지를 `requirements.txt`로 내보내기:
```bash
pip freeze > requirements.txt
```

> **주의**: `pip freeze`는 모든 패키지(하위 의존성 포함)를 출력하므로, 프로젝트에 직접 사용하는 패키지만 선별해 정리하는 것이 좋습니다.

### 개발용 패키지 분리
`requirements-dev.txt` 파일을 만들어 테스트/개발 도구만 별도 관리:
```txt
# requirements-dev.txt
pytest==7.4.3
pytest-asyncio==0.21.1
black==23.11.0
flake8==6.1.0
mypy==1.7.0
```

설치:
```bash
pip install -r requirements.txt -r requirements-dev.txt
```

### 의존성 충돌 해결
패키지 간 버전 충돌이 발생하면:
1. 최신 버전으로 업그레이드 시도:
   ```bash
   pip install --upgrade 패키지명
   ```
2. 충돌하는 패키지를 제거 후 재설치:
   ```bash
   pip uninstall 패키지명
   pip install 패키지명==버전
   ```
3. 가상환경을 새로 만들고 처음부터 설치:
   ```bash
   deactivate
   rmdir /s .venv  # Windows
   rm -rf .venv    # Linux/macOS
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

## Windows 특이사항

### 1. 가상환경 활성화 오류
PowerShell에서 `Activate.ps1` 실행이 차단되는 경우:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 2. C 컴파일러 필요 패키지
일부 패키지(passlib 등)는 C 확장이 필요할 수 있습니다. Windows에서는:
- **Visual C++ Build Tools** 설치 (Microsoft에서 제공)
- 또는 미리 컴파일된 wheel 파일 사용 (pip가 자동으로 선택)

### 3. 경로 문제
Windows에서 경로에 공백이나 한글이 있으면 문제가 될 수 있습니다:
- 프로젝트 경로에 공백/한글 사용 지양
- 예: `C:\Users\3HS_DEV001\Desktop\rag-bot` (권장)

## 일반적인 오류 및 해결

### 오류 1: `pip` 명령을 찾을 수 없음
**해결**: Python이 PATH에 등록되어 있는지 확인
```bash
python --version
python -m pip --version
```

### 오류 2: `Microsoft Visual C++ 14.0 is required`
**해결**: Visual C++ Build Tools 설치 또는 미리 컴파일된 wheel 사용
```bash
pip install --only-binary :all: 패키지명
```

### 오류 3: `chromadb` 설치 실패
**해결**: ChromaDB는 의존성이 많으므로 순차적으로 설치
```bash
pip install chromadb --no-cache-dir
```

### 오류 4: 패키지 버전 충돌
**해결**: `requirements.txt`에서 충돌하는 패키지 버전을 조정하거나, 최신 버전으로 업그레이드

## 다음 단계
- 설치가 완료되면 [`implementation/rag-pipeline.md`](../implementation/rag-pipeline.md)를 따라 RAG 파이프라인을 구축하세요.
- 문제가 발생하면 [`troubleshooting.md`](troubleshooting.md)를 참고하세요.

---

## 참고 자료
- [pip 공식 문서](https://pip.pypa.io/en/stable/)
- [Python 가상환경 가이드](https://docs.python.org/3/tutorial/venv.html)
- [FastAPI 설치 가이드](https://fastapi.tiangolo.com/#installation)
- [LangChain 설치 가이드](https://python.langchain.com/docs/get_started/installation)

