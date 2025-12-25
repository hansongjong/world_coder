import asyncio
from typing import Dict, Any
from telethon import TelegramClient
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch
from src.core.serverless.handler import BaseFunction
from src.core.config import settings

class ScraperFunction(BaseFunction):
    """
    Code: FN_GROUP_SCRAPER_V1
    Desc: Extract members from a target group
    """
    def handle(self, event: Dict[str, Any]) -> Dict[str, Any]:
        group_link = event.get("group_link")
        limit = event.get("limit", 100)
        session_file = event.get("session_file")
        
        self.audit("SCRAPE_START", f"Target: {group_link}, Limit: {limit}")
        
        async def _run():
            session_path = settings.BASE_DIR / "sessions" / session_file
            client = TelegramClient(str(session_path), settings.TG_API_ID, settings.TG_API_HASH)
            
            async with client:
                entity = await client.get_entity(group_link)
                participants = []
                async for user in client.iter_participants(entity, limit=limit):
                    if user.username or user.phone:
                        participants.append({
                            "id": user.id,
                            "username": user.username,
                            "first_name": user.first_name
                        })
                return {"count": len(participants), "data": participants}

        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(_run())
        finally:
            loop.close()