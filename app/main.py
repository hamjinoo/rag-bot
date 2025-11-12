from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from app.vector_store import search_documents
from app.llm import generate_answer
import uvicorn

app = FastAPI(title="RAG 챗봇 API")

class QuestionRequest(BaseModel):
    question: str

@app.get("/")
def health_check():
    return {"status": "ok", "message": "RAG 챗봇 서버 실행 중"}

@app.post("/ask")
async def ask_question(request: QuestionRequest):
    """
    질문에 답변하기
    """
    try:
        # 1. 벡터 검색
        results = search_documents(request.question, k=5)
        
        # 2. GPT 답변 생성
        answer_data = await generate_answer(request.question, results)
        
        return JSONResponse(content=answer_data)
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
