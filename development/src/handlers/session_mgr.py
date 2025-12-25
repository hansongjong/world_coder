import asyncio
import os
from datetime import datetime
from typing import Dict, Any
from telethon import TelegramClient
from sqlalchemy.orm import Session
from src.database.engine import SessionLocal
from src.core.serverless.handler import BaseFunction
from src.core.config import settings
from src.core.database.v3_extensions import TgSession

class SessionValidateFunction(BaseFunction):
    """
    Code: FN_SESSION_VALIDATE
    Description: 세션 파일의 유효성 검사 및 정보 갱신
    """
    
    def handle(self, event: Dict[str, Any]) -> Dict[str, Any]:
        session_id = event.get("session_id")
        proxy_url = event.get("proxy_url", None) # Optional update
        
        self.audit("SESSION_CHECK_START", f"Checking session {session_id}")
        
        # 동기 DB 세션 사용 (Serverless 환경 가정)
        db: Session = SessionLocal()
        try:
            tg_session = db.query(TgSession).filter_by(session_id=session_id).first()
            if not tg_session:
                return {"status": "error", "message": "Session not found in DB"}
            
            # 프록시 업데이트 요청이 있으면 갱신
            if proxy_url:
                tg_session.proxy_url = proxy_url
            
            # 비동기 검증 실행
            loop = asyncio.new_event_loop()
            result = loop.run_until_complete(self._check_telegram(tg_session))
            loop.close()
            
            # DB 업데이트
            tg_session.status = result["status"]
            if result["status"] == "ACTIVE":
                tg_session.username = result.get("username")
                tg_session.first_name = result.get("first_name")
            
            tg_session.last_check_time = datetime.now().isoformat()
            db.commit()
            
            return result
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
        finally:
            db.close()

    async def _check_telegram(self, session_obj: TgSession) -> Dict[str, Any]:
        """Telethon을 이용한 실제 연결 테스트"""
        try:
            # 프록시 설정 파싱 (구현 생략, 필요시 python-socks 사용)
            connection_args = {} 
            
            client = TelegramClient(
                session_obj.session_file_path,
                settings.TG_API_ID,
                settings.TG_API_HASH,
                **connection_args
            )
            
            await client.connect()
            
            if not await client.is_user_authorized():
                await client.disconnect()
                return {"status": "INVALID", "message": "User not authorized"}
            
            me = await client.get_me()
            await client.disconnect()
            
            return {
                "status": "ACTIVE",
                "username": me.username,
                "first_name": me.first_name,
                "user_id": me.id
            }
            
        except Exception as e:
            return {"status": "ERROR", "message": str(e)}