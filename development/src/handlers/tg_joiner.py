import asyncio
from typing import Dict, Any
from telethon import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest
from src.core.serverless.handler import BaseFunction
from src.core.config import settings

class JoinerFunction(BaseFunction):
    """
    Code: FN_CHANNEL_JOINER_V1
    Desc: Auto join channels/groups
    """
    def handle(self, event: Dict[str, Any]) -> Dict[str, Any]:
        target_links = event.get("targets", [])
        session_file = event.get("session_file")
        
        self.audit("JOIN_BATCH_START", f"Count: {len(target_links)}")
        
        async def _run():
            session_path = settings.BASE_DIR / "sessions" / session_file
            client = TelegramClient(str(session_path), settings.TG_API_ID, settings.TG_API_HASH)
            
            results = {}
            async with client:
                for link in target_links:
                    try:
                        await client(JoinChannelRequest(link))
                        results[link] = "Joined"
                        # 딜레이 필요 (FloodWait 방지) - 여기선 생략
                        await asyncio.sleep(2) 
                    except Exception as e:
                        results[link] = f"Failed: {str(e)}"
            
            return results

        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(_run())
        finally:
            loop.close()