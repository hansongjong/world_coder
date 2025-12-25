import asyncio
from telethon import TelegramClient
from src.services.base import BaseTGService
from src.core.config import settings

class TgSenderService(BaseTGService):
    """
    Code: TG_SENDER_BASIC
    기능: 지정된 수신자 리스트에 메시지를 순차 발송
    설정요구: api_id, api_hash, session_name, targets(list), message(str)
    """
    def __init__(self, deployment_id, config, db):
        super().__init__(deployment_id, config, db)
        self.client = None
        
    async def setup(self):
        # 설정에서 필수 값 추출
        api_id = self.config.get("api_id")
        api_hash = self.config.get("api_hash")
        session_name = f"session_{self.deployment_id}"
        
        # 세션 경로는 안전한 곳에 저장
        session_path = settings.BASE_DIR / "sessions" / session_name
        
        self.client = TelegramClient(str(session_path), api_id, api_hash)
        await self.client.connect()
        
        # 인증 확인 (실제로는 여기서 로그인 프로세스가 필요할 수 있음)
        if not await self.client.is_user_authorized():
            # 자동화된 봇 토큰 로그인 or Exception
            bot_token = self.config.get("bot_token")
            if bot_token:
                await self.client.start(bot_token=bot_token)
            else:
                raise Exception("Client is not authorized and no bot token provided.")

    async def run(self):
        targets = self.config.get("targets", [])
        message_text = self.config.get("message", "")
        delay = self.config.get("delay", 2)
        
        if not targets or not message_text:
            self.log("No targets or message content provided.", level="WARNING")
            return

        success_count = 0
        fail_count = 0

        for target in targets:
            try:
                await self.client.send_message(target, message_text)
                success_count += 1
                self.log(f"Sent to {target}")
            except Exception as e:
                fail_count += 1
                self.log(f"Failed to send to {target}: {e}", level="ERROR")
            
            await asyncio.sleep(delay)
            
        self.log(f"Task Finished. Success: {success_count}, Failed: {fail_count}")

    async def cleanup(self):
        if self.client:
            await self.client.disconnect()
            self.log("Telegram Client disconnected.")