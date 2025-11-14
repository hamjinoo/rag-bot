import warnings
import logging
import sys
import os
from contextlib import contextmanager
from io import StringIO

# ChromaDB 텔레메트리 경고 무시 (import 전에 설정)
warnings.filterwarnings("ignore", category=UserWarning, module="chromadb")
warnings.filterwarnings("ignore", message=".*Failed to send telemetry event.*")

# ChromaDB 로거 레벨 조정
logging.getLogger("chromadb").setLevel(logging.ERROR)

# 텔레메트리 비활성화 환경 변수 설정 (import 전)
os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")

# stderr 필터링 (ChromaDB import 시 경고 억제)
_original_stderr = sys.stderr

class FilteredStderr:
    """ChromaDB 텔레메트리 오류만 필터링하는 stderr wrapper"""
    def __init__(self, original):
        self.original = original
        
    def write(self, text):
        # ChromaDB 텔레메트리 오류 메시지가 아니면 출력
        if "Failed to send telemetry event" not in text:
            self.original.write(text)
            
    def flush(self):
        self.original.flush()
        
    def __getattr__(self, name):
        return getattr(self.original, name)

# ChromaDB import 전에 stderr 필터링 설정
sys.stderr = FilteredStderr(_original_stderr)

# 이제 ChromaDB 모듈 import (경고 억제됨)
from fastapi import FastAPI, Request
from app.clients.telegram import send_message, send_typing
from app.formatters.telegram import format_answer
from app.vector_store import search_documents
from app.llm import generate_answer

# stderr 복원
sys.stderr = _original_stderr

app = FastAPI()

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
        return {"ok": False, "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
