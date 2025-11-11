from pathlib import Path
from .pdf import parse_pdf

def parse_document(file_path: str):
  """
  파일 확장자에 따라 적절한 파서 선택
  """
  ext = Path(file_path).suffix.lower()
  
  if
