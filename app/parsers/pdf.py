from pypdf import PdfReader
from typing import Tuple, Dict

def parse_pdf(file_path:str) -> Tuple[str, Dict]:
  """
  PDF 파일을 읽어서 텍스트와 메타데이터 반환
  
  Args:
    file_path: PDF 파일 경로
    
  Returns:
    (전체 텍스트, 메타데이터 딕셔너리)
  """
  reader = PdfReader(file_path)
  
  # 모든 페이지를 \n \n으로 구분해서 합침
  text = "\n\n".join(
    page.extract_text()
    for page in reder.pages
  )
  
  metadata = {
    "doc_id": file_path.split("/")[-1],
    "title": file_path.split("/")[-1],
    "source_path": file_path,
    "page_count": len(reader.pages),  # 페이지 수 추가
  }
  
  return text, metadata
