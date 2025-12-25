from telethon import TelegramClient
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch
from src.services.base import BaseTGService
from src.core.config import settings

class TgScraperService(BaseTGService):
    """
    Code: TG_GROUP_SCRAPER
    기능: 공개/비공개 그룹의 멤버 리스트 추출
    """
    def __init__(self, deployment_id, config, db):
        super().__init__(deployment_id, config, db)
        self.client = None

    async def setup(self):
        # Sender와 동일한 연결 로직 (추후 공통 모듈로 분리 가능)
        api_id = self.config.get("api_id")
        api_hash = self.config.get("api_hash")
        session_name = f"session_{self.deployment_id}"
        session_path = settings.BASE_DIR / "sessions" / session_name
        
        self.client = TelegramClient(str(session_path), api_id, api_hash)
        await self.client.connect()
        
        if not await self.client.is_user_authorized():
             raise Exception("Client not authorized.")

    async def run(self):
        group_url = self.config.get("group_url")
        limit = self.config.get("limit", 100)
        
        self.log(f"Scraping group: {group_url} (Limit: {limit})")
        
        try:
            # 그룹 엔티티 확보
            entity = await self.client.get_entity(group_url)
            
            participants = []
            async for user in self.client.iter_participants(entity, limit=limit):
                user_data = {
                    "id": user.id,
                    "username": user.username,
                    "first_name": user.first_name,
                    "phone": user.phone
                }
                participants.append(user_data)
            
            # 결과 저장 (여기서는 로그에 남기지만, 실제로는 파일이나 Result DB에 저장)
            self.log(f"Scraped {len(participants)} users.")
            # 예: self.save_results(participants)
            
        except Exception as e:
            self.log(f"Scraping failed: {e}", level="ERROR")
            raise e

    async def cleanup(self):
        if self.client:
            await self.client.disconnect()