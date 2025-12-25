import asyncio
from typing import Dict, Any
from telethon import TelegramClient
from src.core.serverless.handler import BaseFunction
from src.core.config import settings

# 공통 헬퍼: 클라이언트 생성
def get_client(session_name: str):
    session_path = settings.BASE_DIR / "sessions" / session_name
    return TelegramClient(str(session_path), settings.TG_API_ID, settings.TG_API_HASH)

class RequestCodeFunction(BaseFunction):
    """
    FN_AUTH_REQUEST_CODE
    전화번호를 받아 인증 코드를 요청합니다.
    """
    def handle(self, event: Dict[str, Any]) -> Dict[str, Any]:
        phone = event.get("phone")
        session_name = event.get("session_name", phone) # 세션 파일명은 전화번호로 통일 권장
        
        self.audit("AUTH_REQ_START", f"Requesting code for {phone}")
        
        async def _async_run():
            client = get_client(session_name)
            await client.connect()
            
            if not await client.is_user_authorized():
                # 코드 발송 요청
                phone_code_hash = await client.send_code_request(phone)
                await client.disconnect()
                return {
                    "status": "pending_verification",
                    "phone_code_hash": phone_code_hash.phone_code_hash,
                    "session_name": session_name
                }
            else:
                await client.disconnect()
                return {"status": "already_authorized", "msg": "Session is valid."}

        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(_async_run())
        finally:
            loop.close()

class SubmitCodeFunction(BaseFunction):
    """
    FN_AUTH_SUBMIT_CODE
    사용자가 입력한 코드를 받아 로그인을 완료합니다.
    """
    def handle(self, event: Dict[str, Any]) -> Dict[str, Any]:
        phone = event.get("phone")
        code = event.get("code")
        phone_code_hash = event.get("phone_code_hash")
        session_name = event.get("session_name", phone)
        
        self.audit("AUTH_SUBMIT_START", f"Submitting code for {phone}")
        
        async def _async_run():
            client = get_client(session_name)
            await client.connect()
            
            try:
                # 로그인 시도
                user = await client.sign_in(phone=phone, code=code, phone_code_hash=phone_code_hash)
                await client.disconnect()
                return {
                    "status": "success",
                    "user_id": user.id,
                    "username": user.username
                }
            except Exception as e:
                await client.disconnect()
                raise e

        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(_async_run())
        finally:
            loop.close()