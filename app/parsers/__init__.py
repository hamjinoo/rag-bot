from pathlib import Path
from .pdf import parse_pdf

def parse_document(file_path: str):
    """
    파일 확장자에 따라 적절한 파서 선택
    """
    ext = Path(file_path).suffix.lower()
    
    if ext == ".pdf":
        return parse_pdf(file_path)
    elif ext == ".docx":
        from .docx_parser import parse_docx
        return parse_docx(file_path)
    elif ext == ".csv":
        from .csv_parser import parse_csv
        return parse_csv(file_path)
    else:
        raise ValueError(f"지원하지 않는 파일 형식: {ext}")
