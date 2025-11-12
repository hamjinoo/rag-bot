from app.vector_store import vector_client
from app.llm import generate_answer

async def retrieve_answer(question: str) -> dict:
    # score_threshold 없이 검색 후 필터링
    docs_with_scores = vector_client.similarity_search_with_score(
        question,
        k=5,
    )
    
    # 거리 점수를 유사도로 변환하고 최소 유사도 0.3 이상만 선택
    filtered_docs = []
    for doc, distance in docs_with_scores:
        similarity = max(0.0, 1.0 - (distance / 2.0))
        if similarity >= 0.3:  # 유사도 30% 이상
            filtered_docs.append(doc)
    
    if not filtered_docs:
        return {
            "answer": "자료에서 근거를 찾지 못했습니다. 관련 문서를 업로드해 주세요.",
            "sources": [],
        }
    return await generate_answer(question, filtered_docs)
