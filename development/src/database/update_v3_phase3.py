import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from sqlalchemy.orm import Session
from src.database.engine import engine
from src.core.database.v3_schema import FunctionCatalog
from src.core.database.v3_campaigns import Campaign

def update_phase3():
    print("[*] Applying Phase 3: Campaign & Scheduler...")
    
    # 1. 테이블 생성
    Campaign.__table__.create(bind=engine, checkfirst=True)
    
    session = Session(engine)
    try:
        # 2. 디스패처 함수 등록
        fn_code = "FN_CAMPAIGN_DISPATCH"
        if not session.query(FunctionCatalog).filter_by(function_code=fn_code).first():
            new_fn = FunctionCatalog(
                function_code=fn_code,
                function_name="Campaign Dispatcher",
                handler_path="src.handlers.campaign_mgr.CampaignDispatchFunction",
                resource_spec={"timeout": 300, "type": "workflow"},
                is_active=True
            )
            session.add(new_fn)
            print(f"    [+] Function Registered: {fn_code}")
        
        session.commit()
        print("[SUCCESS] Phase 3 Update Complete.")
        
    except Exception as e:
        session.rollback()
        print(f"[ERROR] Phase 3 Update Failed: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    update_phase3()