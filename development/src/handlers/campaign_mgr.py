import uuid
import math
from datetime import datetime
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from src.database.engine import SessionLocal
from src.core.serverless.handler import BaseFunction
from src.core.database.v3_extensions import TgSession, TargetList
from src.core.database.v3_campaigns import Campaign
from src.core.database.v3_schema import ExecutionRequest

class CampaignDispatchFunction(BaseFunction):
    """
    Code: FN_CAMPAIGN_DISPATCH
    Description: 캠페인을 실행하여 작업을 개별 세션에게 분배(Sharding)합니다.
    """
    
    def handle(self, event: Dict[str, Any]) -> Dict[str, Any]:
        campaign_id = event.get("campaign_id")
        self.audit("CAMPAIGN_START", f"Dispatching Campaign {campaign_id}")
        
        db: Session = SessionLocal()
        try:
            # 1. 캠페인 로드
            campaign = db.query(Campaign).filter_by(campaign_id=campaign_id).first()
            if not campaign:
                return {"status": "error", "message": "Campaign not found"}
            
            # 상태 변경
            campaign.status = "RUNNING"
            campaign.start_time = datetime.now()
            db.commit()
            
            # 2. 타겟 데이터 로드 (메모리 효율을 위해 실제로는 Chunk로 읽어야 함)
            target_list = db.query(TargetList).filter_by(list_id=campaign.target_list_id).first()
            if not target_list:
                raise Exception("Target List not found")
            
            # 파일에서 타겟 읽기 (간소화된 로직)
            with open(target_list.file_path, "r", encoding="utf-8") as f:
                targets = [line.strip() for line in f if line.strip()]
            
            # 3. 가용 세션 로드
            sessions = db.query(TgSession).filter(
                TgSession.user_id == campaign.user_id,
                TgSession.status == "ACTIVE"
            ).all()
            
            if not sessions:
                raise Exception("No Active Sessions available")
            
            # 4. 분배 로직 (Round Robin or Chunking)
            # 여기서는 세션당 N명씩 할당하는 Chunk 방식 사용
            total_targets = len(targets)
            session_count = len(sessions)
            
            # 단순 균등 분배
            chunk_size = math.ceil(total_targets / session_count)
            dispatched_tasks = 0
            
            for i, session in enumerate(sessions):
                start_idx = i * chunk_size
                end_idx = start_idx + chunk_size
                batch_targets = targets[start_idx:end_idx]
                
                if not batch_targets:
                    break
                
                # 5. 하위 실행 요청 생성 (FN_MSG_SENDER_V1 호출)
                task_payload = {
                    "targets": batch_targets,
                    "message": campaign.config.get("message"),
                    "session_file": session.session_file_path,
                    "delay": campaign.config.get("delay", 5)
                }
                
                new_req = ExecutionRequest(
                    req_id=f"sub-{uuid.uuid4()}",
                    function_code="FN_MSG_SENDER_V1", # Phase 1에서 만든 함수
                    user_id=campaign.user_id,
                    input_payload=task_payload,
                    status="QUEUED"
                )
                db.add(new_req)
                dispatched_tasks += 1
            
            campaign.total_targets = total_targets
            db.commit()
            
            return {
                "status": "success", 
                "dispatched_batches": dispatched_tasks,
                "total_targets": total_targets
            }

        except Exception as e:
            if campaign:
                campaign.status = "FAILED"
                db.commit()
            return {"status": "error", "message": str(e)}
        finally:
            db.close()