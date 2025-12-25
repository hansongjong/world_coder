import asyncio
import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from src.database.engine import SessionLocal
from src.core.database.v3_campaigns import Campaign
from src.core.database.v3_schema import ExecutionRequest
from src.core.logger import logger

async def scheduler_tick():
    """
    주기적으로 실행되며 SCHEDULED 상태인 캠페인을 확인합니다.
    """
    logger.debug("[Scheduler] Tick...")
    db: Session = SessionLocal()
    try:
        now = datetime.now()
        
        # 시작 시간이 지난 'SCHEDULED' 캠페인 조회
        pending_campaigns = db.query(Campaign).filter(
            Campaign.status == "SCHEDULED",
            Campaign.scheduled_at <= now
        ).all()
        
        for campaign in pending_campaigns:
            logger.info(f"[Scheduler] Triggering Campaign: {campaign.name} ({campaign.campaign_id})")
            
            # Dispatcher 함수 실행 요청 생성
            req_id = f"sch-{uuid.uuid4()}"
            exec_req = ExecutionRequest(
                req_id=req_id,
                function_code="FN_CAMPAIGN_DISPATCH",
                user_id=campaign.user_id,
                input_payload={"campaign_id": campaign.campaign_id},
                status="QUEUED"
            )
            db.add(exec_req)
            
            # 중복 실행 방지를 위해 상태 변경
            campaign.status = "PROCESSING" 
            
        db.commit()
        
    except Exception as e:
        logger.error(f"[Scheduler] Error: {e}")
    finally:
        db.close()

async def run_scheduler():
    logger.info("[Scheduler] Service Started.")
    while True:
        await scheduler_tick()
        await asyncio.sleep(60) # 1분 주기