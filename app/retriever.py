from app.vector_store import vector_client
from app.llm import generate_answer

async def retrieve_answer(question: str) -> dict:
    docs = vector_client.similarity_search(
        question,
        k=5,
        score_threshold=0.75,
    )
    if not docs:
        return {
            "answer": "자료에서 근거를 찾지 못했습니다. 관련 문서를 업로드해 주세요.",
            "sources": [],
        }
    return await generate_answer(question, docs)
