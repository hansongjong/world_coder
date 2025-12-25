import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from sqlalchemy.orm import Session
from src.database.engine import engine, Base
from src.commerce.domain.models import Store, Product, Category, CommerceUser, UserRole
from src.commerce.auth.security import get_password_hash

def full_restore():
    print("[*] Running Full System Restore...")
    
    # 1. 테이블 재생성 (깔끔하게 날리고 다시 생성)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    session = Session(engine)
    try:
        # 2. 상점 & 점주 생성
        store = Store(name="TG Cafe Gangnam", address="Seoul", biz_number="12345")
        session.add(store)
        session.flush()
        
        owner = CommerceUser(
            username="owner",
            password_hash=get_password_hash("1234"),
            role=UserRole.OWNER,
            store_id=store.id
        )
        session.add(owner)
        
        # 3. 메뉴 생성
        cats = {
            "coffee": Category(store_id=store.id, name="Coffee", display_order=1),
            "dessert": Category(store_id=store.id, name="Dessert", display_order=2),
        }
        session.add_all(cats.values())
        session.flush()
        
        prods = [
            Product(category_id=cats["coffee"].id, name="Americano", price=4500),
            Product(category_id=cats["coffee"].id, name="Latte", price=5000),
            Product(category_id=cats["coffee"].id, name="Vanilla Latte", price=5500),
            Product(category_id=cats["dessert"].id, name="Cheesecake", price=6500),
            Product(category_id=cats["dessert"].id, name="Brownie", price=4000),
        ]
        session.add_all(prods)
        
        session.commit()
        print("[SUCCESS] DB Restored. User 'owner' / '1234' is ready.")
        
    except Exception as e:
        print(f"[ERROR] Restore failed: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    full_restore()