from app.parsers import parse_document
from app.pipelines import split_text

def test_chunking():
    # 1. PDF 파싱
    text, metadata = parse_document("data/sample.pdf")
    print(f"📄 원본 텍스트: {len(text)}자")
    
    # 2. 청크 분할
    chunks = split_text(text, metadata)
    print(f"🔪 청크 개수: {len(chunks)}개")
    
    # 3. 첫 청크 확인
    print(f"\n📌 첫 번째 청크 (600자):")
    print(chunks[0].page_content[:200] + "...")
    
    # 4. 오버랩 확인
    if len(chunks) >= 2:
        chunk1_end = chunks[0].page_content[-50:]
        chunk2_start = chunks[1].page_content[:50:]
        print(f"\n🔗 청크1 끝: ...{chunk1_end}")
        print(f"🔗 청크2 시작: {chunk2_start}...")

if __name__ == "__main__":
    test_chunking()
