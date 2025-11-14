import base64
import hmac
import hashlib
import os
from dotenv import load_dotenv

load_dotenv()

SECRET = os.getenv("KAKAO_CHANNEL_SECRET")

def verify_signature(body: bytes, signature: str) -> bool:
    """
    카카오 요청 시그니처 검증
    
    Args:
        body: 요청 본문 (bytes)
        signature: X-Kakao-Signature 헤더 값
        
    Returns:
        True: 검증 성공, False: 검증 실패
    """
    if not SECRET:
        return False
    
    # HMAC-SHA256으로 해시 생성
    mac = hmac.new(
        SECRET.encode("utf-8"),
        body,
        hashlib.sha256
    )
    digest = base64.b64encode(mac.digest()).decode("utf-8")
    
    # 시그니처 비교 (타이밍 공격 방지)
    return hmac.compare_digest(digest, signature)
