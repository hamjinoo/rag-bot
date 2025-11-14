import warnings
import logging
import sys
import os
import asyncio
import json
from fastapi import FastAPI, Request
from app.security.kakao import verify_signature
from app.formatters.kakao import format_skill_response, format_error_response
from app.vector_store import search_documents
from app.llm import generate_answer

# ChromaDB 텔레메트리 경고 무시 (import 전에 설정)
warnings.filterwarnings("ignore", category=UserWarning, module="chromadb")
warnings.filterwarnings("ignore", message=".*Failed to send telemetry event.*")

# ChromaDB 로거 레벨 조정
logging.getLogger("chromadb").setLevel(logging.ERROR)

# 텔레메트리 비활성화 환경 변수 설정
os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")

# FastAPI 앱 초기화
app = FastAPI(title="RAG 챗봇 API")

@app.get("/")
def health_check():
    """헬스 체크 엔드포인트"""
    return {"status": "ok", "message": "RAG 챗봇 서버 실행 중"}

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
        
        # JSON 파싱 (body를 직접 파싱)
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
