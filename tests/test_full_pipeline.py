from app.parsers import parse_document
from app.pipelines import split_text
from app.vector_store import add_documents, search_documents

def test_full_pipeline():
    print("📂 Step 1: PDF 파싱")
    text, metadata = parse_document("data/sample.pdf")
    print(f"   ✅ {len(text)}자 추출\n")
    
    print("🔪 Step 2: 청크 분할")
    chunks = split_text(text, metadata)
    print(f"   ✅ {len(chunks)}개 청크 생성\n")
    
    print("🗄️ Step 3: 벡터 DB 색인 (임베딩 생성 중... 30초 소요)")
    # 테스트 시 기존 데이터 삭제 (중복 방지)
    add_documents(chunks, clear_existing=True)
    print(f"   ✅ 색인 완료\n")
    
    print("🔍 Step 4: 검색 테스트")
    # 문서 내용과 관련된 질문들로 테스트
    test_queries = [
        "여기서 제가 무엇을 배울 수 있나요?",
    ]
    
    for query in test_queries:
        print(f"\n   질문: {query}")
        results = search_documents(query, k=5, score_threshold=None)  # k=5로 늘려서 더 많은 결과 확인
        if results:
            # 중복 제거 후 상위 3개만 표시
            unique_results = []
            seen = set()
            for doc, score in results:
                content_preview = doc.page_content[:50]
                if content_preview not in seen:
                    seen.add(content_preview)
                    unique_results.append((doc, score))
                    if len(unique_results) >= 3:
                        break
            
            print(f"   ✅ {len(unique_results)}개 고유 문서 발견:")
            for i, (doc, score) in enumerate(unique_results, 1):
                preview = doc.page_content[:80].replace("\n", " ")
                print(f"      {i}. 유사도 {score:.3f}: {preview}...")
        else:
            print("   ❌ 관련 문서를 찾지 못했습니다.")

if __name__ == "__main__":
    test_full_pipeline()
