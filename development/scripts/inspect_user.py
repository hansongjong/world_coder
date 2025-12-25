import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from sqlalchemy.orm import Session
from src.database.engine import engine
from src.commerce.domain.models import CommerceUser
from src.commerce.auth.security import verify_password, get_password_hash

def inspect():
    session = Session(engine)
    try:
        user = session.query(CommerceUser).filter_by(username="owner").first()
        
        print("\n=== USER INSPECTION ===")
        if not user:
            print("❌ User 'owner' NOT FOUND in DB!")
            # 복구 시도
            print("[*] Creating emergency user...")
            # ... (생략, full_restore 사용 권장)
            return

        print(f"✅ User Found: ID={user.id}, Role={user.role}")
        print(f"   Hash stored: {user.password_hash[:20]}...")
        
        # 비밀번호 검증 테스트
        test_pw = "1234"
        is_valid = verify_password(test_pw, user.password_hash)
        
        if is_valid:
            print(f"✅ Password '{test_pw}' matches hash.")
        else:
            print(f"❌ Password '{test_pw}' DOES NOT match hash.")
            print("   -> Resetting password to '1234'...")
            user.password_hash = get_password_hash("1234")
            session.commit()
            print("   [FIXED] Password reset complete.")
            
    finally:
        session.close()

if __name__ == "__main__":
    inspect()