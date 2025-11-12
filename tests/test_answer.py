import asyncio
from app.vector_store import search_documents
from app.llm import generate_answer

async def test_answer():
    query = "Prim 알고리즘이 뭐야?"
    
    print(f"🔍 검색 중: {query}")
    results = search_documents(query, k=3)
    
    print(f"🤖 GPT 답변 생성 중...")
    answer_data = await generate_answer(query, results)
    
    print("\n" + "="*60)
    print(f"질문: {query}")
    print("="*60)
    print(answer_data["answer"])
    print("\n출처:")
    for src in answer_data["sources"]:
        print(f"  - {src['title']} (유사도: {src['score']})")

if __name__ == "__main__":
    asyncio.run(test_answer())
