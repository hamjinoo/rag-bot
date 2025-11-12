from app.parsers import parse_document

def test_pdf_parser():
    # 테스트용 PDF 준비 (구글에서 "샘플 PDF" 다운로드)
    text, metadata = parse_document("data/sample.pdf")
    
    assert len(text) > 0, "텍스트가 비어있습니다"
    assert metadata["page_count"] > 0, "페이지 수가 0입니다"
    print(f"✅ 파싱 성공: {len(text)}자, {metadata['page_count']}페이지")

if __name__ == "__main__":
    test_pdf_parser()
