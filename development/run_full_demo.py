import asyncio
import time
import uuid
import sys
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

# 프로젝트 경로 설정
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent))

from src.database.engine import init_db, SessionLocal
from src.database.init_v3 import init_v3_system
from src.database.update_v3_phase2 import update_phase2
from src.database.update_v3_phase3 import update_phase3
from src.database.update_catalog import update_catalog

from src.core.database.v3_schema import MasterUser, FunctionCatalog, ExecutionRequest
from src.core.database.v3_extensions import TgSession, TargetList
from src.core.database.v3_campaigns import Campaign
from src.core.kernel import SystemKernel

def print_step(msg):
    print(f"\n{'='*50}\n[DEMO] {msg}\n{'='*50}")

def setup_environment():
    print_step("1. System Initialization")
    # 모든 DB 스키마 및 카탈로그 초기화
    init_v3_system()
    update_phase2()
    update_phase3()
    update_catalog()
    print("   [OK] Database & Catalog Ready.")

def create_mock_assets(db: Session, user_id: str):
    print_step("2. Creating Mock Assets (Session & Data)")
    
    # 1. 가짜 세션 생성
    for i in range(3):
        sess = TgSession(
            session_id=f"sess_{i}",
            user_id=user_id,
            phone=f"+82100000000{i}",
            session_file_path=f"sessions/mock_{i}.session",
            status="ACTIVE",
            username=f"mock_user_{i}"
        )
        db.add(sess)
    print("   [OK] 3 Active Sessions Created.")
    
    # 2. 가짜 타겟 리스트 생성
    # 파일 생성 시늉
    mock_file = Path("data/demo_targets.txt")
    mock_file.parent.mkdir(exist_ok=True)
    with open(mock_file, "w") as f:
        f.write("\n".join([f"user_{x}" for x in range(100)]))
        
    t_list = TargetList(
        list_id="list_demo_001",
        user_id=user_id,
        name="Demo Target 100",
        source_type="UPLOAD",
        total_count=100,
        file_path=str(mock_file)
    )
    db.add(t_list)
    print("   [OK] Target List (100 users) Created.")
    db.commit()

def run_campaign_simulation(db: Session, user_id: str):
    print_step("3. Launching Marketing Campaign")
    
    # 1. 캠페인 생성
    camp_id = f"camp_{uuid.uuid4().hex[:8]}"
    campaign = Campaign(
        campaign_id=camp_id,
        user_id=user_id,
        name="🚀 Grand Opening Demo",
        status="SCHEDULED",
        target_list_id="list_demo_001",
        config={"message": "Hello World", "delay": 1},
        scheduled_at=datetime.now() # 즉시 실행
    )
    db.add(campaign)
    db.commit()
    print(f"   [OK] Campaign '{campaign.name}' Scheduled.")
    
    # 2. 스케줄러 시뮬레이션 (1회 Tick)
    print_step("4. Scheduler Tick (Triggering Campaign)")
    
    # 스케줄러 로직 수동 실행
    from src.core.scheduler import scheduler_tick
    # 비동기 함수 실행을 위해 loop 사용
    loop = asyncio.new_event_loop()
    loop.run_until_complete(scheduler_tick())
    
    # 상태 확인
    db.refresh(campaign)
    print(f"   [CHECK] Campaign Status: {campaign.status}")
    
    if campaign.status == "PROCESSING":
        # Dispatcher가 만든 하위 작업 확인
        jobs = db.query(ExecutionRequest).filter(ExecutionRequest.function_code == "FN_MSG_SENDER_V1").all()
        print(f"   [RESULT] Dispatcher created {len(jobs)} sub-tasks (batches) for sending.")

def main():
    db = SessionLocal()
    try:
        setup_environment()
        
        # 관리자 계정 확보
        admin = db.query(MasterUser).filter_by(username="admin").first()
        if not admin:
            print("[ERROR] Admin user not found.")
            return

        create_mock_assets(db, admin.user_id)
        run_campaign_simulation(db, admin.user_id)
        
        print_step("5. Demo Complete")
        print("Now run 'python src/interface/cli_dashboard.py' to see the results visually!")
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main()