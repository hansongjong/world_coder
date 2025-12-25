import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from sqlalchemy.orm import Session
from src.database.engine import engine, init_db
from src.core.database.v3_schema import Base, MasterUser
from src.core.security import get_password_hash

def init_phase1_security():
    print("[*] Phase 1: Initializing Security & Admin User...")
    
    # 테이블 재생성 (스키마 변경 반영을 위해)
    # 주의: 개발 환경이므로 기존 데이터를 날릴 수 있습니다. 운영 환경 주의.
    Base.metadata.create_all(bind=engine)
    
    session = Session(engine)
    try:
        # Admin 계정 확인 및 생성
        admin_username = "admin"
        admin_password = "admin_password" # 실제 운영 시 변경 필수
        
        existing_admin = session.query(MasterUser).filter_by(username=admin_username).first()
        
        if not existing_admin:
            new_admin = MasterUser(
                user_id="root-admin-001",
                username=admin_username,
                email="root@tg-system.com",
                hashed_password=get_password_hash(admin_password),
                tier_level="ENTERPRISE",
                is_active=True
            )
            session.add(new_admin)
            session.commit()
            print(f"    [SUCCESS] Admin Created.")
            print(f"    Username: {admin_username}")
            print(f"    Password: {admin_password}")
        else:
            print("    [INFO] Admin already exists.")
            
    except Exception as e:
        print(f"    [ERROR] {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    init_phase1_security()