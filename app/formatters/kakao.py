def format_skill_response(answer: str, sources: list[dict]) -> dict:
    """
    RAG 답변을 카카오 스킬 응답 포맷으로 변환
    
    카카오 스킬 응답 형식:
    {
      "version": "2.0",
      "template": {
        "outputs": [
          {
            "simpleText": {
              "text": "답변 내용"
            }
          }
        ]
      }
    }
    """
    # 출처 목록 생성
    source_text = "\n\n📚 출처:\n"
    for src in sources:
        title = src.get("title", "문서")
        page = src.get("page", "?")
        source_text += f"• {title} (p.{page})\n"
    
    return {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": f"{answer}{source_text}"
                    }
                }
            ]
        }
    }

def format_error_response(error_msg: str) -> dict:
    """
    에러 응답 포맷
    """
    return {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": f"❌ {error_msg}\n\n잠시 후 다시 시도해 주세요."
                    }
                }
            ]
        }
    }
