def format_answer(answer: str, sources: list[dict]) -> str:
    """
    RAG 답변을 텔레그램 Markdown 포맷으로 변환
    
    텔레그램 Markdown 규칙:
    - **굵게**: **text**
    - _기울임_: _text_
    - `코드`: `code`
    - [링크](url): [text](url)
    - 특수문자 이스케이프: _ → \_, * → \*
    """
    # 출처 목록 생성
    source_text = "\n\n*출처:*\n"
    for src in sources:
        title = src.get("title", "문서")
        page = src.get("page", "?")
        source_text += f"• {title} (p.{page})\n"
    
    # Markdown 특수문자 이스케이프
    answer = answer.replace("_", "\\_").replace("*", "\\*")
    
    return f"{answer}{source_text}"

def escape_markdown(text: str) -> str:
    """
    텔레그램 Markdown 특수문자 이스케이프
    """
    special = ["_", "*", "[", "]", "(", ")", "~", "`", ">", "#", "+", "-", "=", "|", "{", "}", ".", "!"]
    for char in special:
        text = text.replace(char, f"\\{char}")
    return text
