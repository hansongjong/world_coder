import asyncio
from telethon import TelegramClient, errors
from src.core.config import settings
from src.core.logger import logger  # 이전 단계의 logger 재사용 가정 (없으면 재생성 필요)
from src.domain.tg_models import TgAccount, AccountStatus

class TgClientManager:
    """
    Telethon Client 생명주기 및 연결 관리
    """
    
    def __init__(self, account: TgAccount):
        self.account = account
        self.session_path = str(settings.SESSION_DIR / account.session_file)
        
        # API ID/HASH는 계정별로 다를 수도 있고, 전역 설정을 쓸 수도 있음
        # 여기서는 전역 설정을 우선 사용하되 계정별 설정이 있으면 그것을 따름
        self.api_id = account.api_id or settings.API_ID
        self.api_hash = account.api_hash or settings.API_HASH
        
        self.client = TelegramClient(
            self.session_path,
            self.api_id,
            self.api_hash
        )

    async def connect(self) -> bool:
        """텔레그램 서버 연결"""
        try:
            await self.client.connect()
            if not await self.client.is_user_authorized():
                logger.warning(f"Account {self.account.phone_number} is NOT authorized.")
                return False
            
            me = await self.client.get_me()
            logger.info(f"Connected as: {me.first_name} ({self.account.phone_number})")
            return True
            
        except OSError as e:
            logger.error(f"Connection Failed (Network/File): {e}")
            return False
        except Exception as e:
            logger.error(f"Unknown Error during connection: {e}")
            return False

    async def disconnect(self):
        await self.client.disconnect()

    async def send_message(self, target: str, message: str):
        """
        메시지 전송 래퍼
        target: username or phone or user_id
        """
        if not self.client.is_connected():
            logger.error("Client not connected.")
            return False

        try:
            await self.client.send_message(target, message)
            logger.success(f"Message sent to {target}")
            return True
            
        except errors.FloodWaitError as e:
            logger.warning(f"FloodWait: Must wait {e.seconds} seconds.")
            # 실제 운영시에는 여기서 대기하거나 작업을 큐로 미루는 로직 필요
            return False
        except errors.RPCError as e:
            logger.error(f"Telegram RPC Error: {e}")
            return False
        except Exception as e:
            logger.error(f"Sending failed: {e}")
            return False