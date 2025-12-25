import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from sqlalchemy.orm import Session
from src.database.engine import engine
from src.core.database.v3_schema import Base, FunctionCatalog, MasterUser

def init_v3_system():
    print("[*] Initializing TG-SYSTEM V3 Schema...")
    
    # 1. 테이블 생성
    Base.metadata.create_all(bind=engine)
    
    session = Session(engine)
    try:
        # 2. 기본 관리자 생성
        if not session.query(MasterUser).filter_by(username="admin").first():
            admin = MasterUser(
                user_id="admin-uuid-001",
                username="admin",
                email="admin@tg-system.com",
                tier_level="ENTERPRISE"
            )
            session.add(admin)
            print("    [+] Admin User Created")

        # 3. 함수 카탈로그(Function Catalog) 등록
        # 시스템이 지원하는 기능들을 여기서 정의합니다.
        functions = [
            {
                "code": "FN_MSG_SENDER_V1",
                "name": "TG Message Sender",
                "handler": "src.handlers.tg_sender.MainFunction",
                "spec": {"timeout": 60, "type": "marketing"}
            },
            {
                "code": "FN_AUTH_REQUEST_CODE",
                "name": "Request Login Code",
                "handler": "src.handlers.auth.RequestCodeFunction",
                "spec": {"timeout": 30, "type": "system"}
            },
            {
                "code": "FN_AUTH_SUBMIT_CODE",
                "name": "Submit Login Code",
                "handler": "src.handlers.auth.SubmitCodeFunction",
                "spec": {"timeout": 30, "type": "system"}
            }
        ]

        for fn in functions:
            if not session.query(FunctionCatalog).filter_by(function_code=fn["code"]).first():
                new_fn = FunctionCatalog(
                    function_code=fn["code"],
                    function_name=fn["name"],
                    handler_path=fn["handler"],
                    resource_spec=fn["spec"],
                    is_active=True
                )
                session.add(new_fn)
                print(f"    [+] Function Registered: {fn['code']}")
        
        session.commit()
        print("[SUCCESS] V3 System Initialized.")
        
    except Exception as e:
        session.rollback()
        print(f"[ERROR] Initialization Failed: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    init_v3_system()