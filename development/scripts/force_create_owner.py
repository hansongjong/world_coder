import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from sqlalchemy.orm import Session
from src.database.engine import engine
from src.commerce.domain.models import CommerceUser, UserRole
from src.commerce.auth.security import get_password_hash

def force_create():
    session = Session(engine)
    try:
        # 기존 owner 삭제 (중복 방지)
        session.query(CommerceUser).filter_by(username="owner").delete()
        session.commit()
        
        # 새로 생성
        user = CommerceUser(
            username="owner",
            password_hash=get_password_hash("1234"),
            role=UserRole.OWNER,
            store_id=1
        )
        session.add(user)
        session.commit()
        print("[SUCCESS] User 'owner' created with password '1234'")
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        session.close()

if __name__ == "__main__":
    force_create()