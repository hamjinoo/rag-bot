from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from typing import List, Tuple, Any
import os
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.2,  # 낮을수록 일관적 (0~1)
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

async def generate_answer(question: str, search_results: List[Tuple[Any, float]]) -> dict:
    """
    검색 결과를 바탕으로 GPT 답변 생성
    
    Args:
        question: 사용자 질문
        search_results: [(Document, score), ...]
        
    Returns:
        {"answer": "...", "sources": [...]}
    """
    if not search_results:
        return {
            "answer": "❌ 관련 문서를 찾지 못했습니다. 문서를 업로드하거나 질문을 구체화해 주세요.",
            "sources": []
        }
    
    # 컨텍스트 구성
    context = "\n\n".join([
        f"[문서 {i+1}] {doc.page_content}"
        for i, (doc, score) in enumerate(search_results)
    ])
    
    # 프롬프트 구성
    system_prompt = """당신은 문서 기반 Q&A 어시스턴트입니다.

규칙:
1. 제공된 컨텍스트 안에서만 답변하세요.
2. 근거가 없으면 "문서에서 찾을 수 없습니다"라고 명시하세요.
3. 답변 끝에 출처를 bullet 리스트로 나열하세요.

출력 형식:
답변 내용...

**출처:**
- [문서명] 참고
"""
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"질문: {question}\n\n컨텍스트:\n{context}")
    ]
    
    # GPT 호출
    response = await llm.apredict_messages(messages)
    
    # 출처 정리
    sources = [
        {
            "title": doc.metadata.get("title", "문서"),
            "page": doc.metadata.get("page_count", "?"),
            "score": round(score, 2)
        }
        for doc, score in search_results
    ]
    
    return {
        "answer": response.content,
        "sources": sources
    }
