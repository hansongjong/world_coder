import asyncio
from typing import Dict, Any
from telethon import TelegramClient
from src.core.serverless.handler import BaseFunction
from src.core.config import settings # 앞서 정의한 config 재사용

class MainFunction(BaseFunction):
    """
    Function Code: FN_MSG_SENDER_V1
    Description: 단발성 텔레그램 메시지 전송 함수
    """
    
    def handle(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Event Payload:
        {
            "target": "+821012345678",
            "message": "Hello Serverless",
            "session_file": "user_123.session"
        }
        """
        target = event.get("target")
        message = event.get("message")
        session_file = event.get("session_file")
        
        self.audit("EXECUTE_START", f"Sending to {target}")
        
        # 비동기 실행을 위한 래퍼
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(self._send_async(session_file, target, message))
            return result
        finally:
            loop.close()

    async def _send_async(self, session_file, target, message):
        # API ID/HASH는 환경변수 또는 보안 저장소(Vault)에서 가져와야 함
        api_id = settings.TG_API_ID
        api_hash = settings.TG_API_HASH
        
        session_path = settings.BASE_DIR / "sessions" / session_file
        
        client = TelegramClient(str(session_path), api_id, api_hash)
        
        async with client:
            await client.send_message(target, message)
            
        return {"status": "success", "sent_to": target}