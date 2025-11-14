import httpx
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

async def send_message(chat_id: int, text: str):
    """
    텔레그램 메시지 전송
    
    Args:
        chat_id: 사용자 채팅 ID
        text: 전송할 텍스트 (Markdown 지원)
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_URL}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "Markdown",  # **굵게**, _기울임_ 지원
            }
        )
        return response.json()

async def send_typing(chat_id: int):
    """
    "입력 중..." 표시 (사용자 경험 향상)
    """
    async with httpx.AsyncClient() as client:
        await client.post(
            f"{API_URL}/sendChatAction",
            json={"chat_id": chat_id, "action": "typing"}
        )
