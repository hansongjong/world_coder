import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from sqlalchemy.orm import Session
from src.database.engine import engine
from src.core.database.v3_schema import Base, FunctionCatalog
from src.core.database.v3_extensions import TgSession, TargetList

def update_phase2():
    print("[*] Applying Phase 2: Resource & Data Management...")
    
    # 1. 확장된 테이블 생성
    # Base는 v3_schema에 있지만, extensions에서 임포트한 모델들도 Base를 공유하므로 create_all 호출 시 생성됨
    # 주의: v3_extensions의 Base가 v3_schema의 Base와 동일한지 확인 필요 (여기선 동일하다고 가정)
    TgSession.__table__.create(bind=engine, checkfirst=True)
    TargetList.__table__.create(bind=engine, checkfirst=True)
    
    session = Session(engine)
    try:
        # 2. 새로운 관리 함수 등록
        new_functions = [
            {
                "code": "FN_SESSION_VALIDATE",
                "name": "Session Validator",
                "handler": "src.handlers.session_mgr.SessionValidateFunction",
                "spec": {"timeout": 60, "type": "management"}
            },
            {
                "code": "FN_DATA_IMPORT",
                "name": "Target Data Import",
                "handler": "src.handlers.data_mgr.DataImportFunction",
                "spec": {"timeout": 120, "type": "management"}
            }
        ]

        for fn in new_functions:
            if not session.query(FunctionCatalog).filter_by(function_code=fn["code"]).first():
                new_fn = FunctionCatalog(
                    function_code=fn["code"],
                    function_name=fn["name"],
                    handler_path=fn["handler"],
                    resource_spec=fn["spec"],
                    is_active=True
                )
                session.add(new_fn)
                print(f"    [+] Phase 2 Function Registered: {fn['code']}")
        
        session.commit()
        print("[SUCCESS] Phase 2 Update Complete.")
        
    except Exception as e:
        session.rollback()
        print(f"[ERROR] Phase 2 Update Failed: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    update_phase2()