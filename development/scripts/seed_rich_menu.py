import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from sqlalchemy.orm import Session
from src.database.engine import engine
from src.commerce.domain.models import Store, Product, Category

def seed_rich_menu():
    session = Session(engine)
    try:
        store = session.query(Store).first()
        if not store:
            print("[ERROR] Store not found. Run seed_commerce_data.py first.")
            return

        print(f"[*] Adding Rich Menu to Store: {store.name}")

        # 1. 기존 메뉴/카테고리 초기화 (중복 방지)
        session.query(Product).delete()
        session.query(Category).delete()
        session.flush()

        # 2. 카테고리 정의
        cats = {
            "coffee": Category(store_id=store.id, name="☕ Coffee & Espresso", display_order=1),
            "signature": Category(store_id=store.id, name="★ Signature", display_order=2),
            "tea": Category(store_id=store.id, name="🍵 Tea & Ade", display_order=3),
            "smoothie": Category(store_id=store.id, name="🥤 Frappe & Smoothie", display_order=4),
            "bakery": Category(store_id=store.id, name="🍰 Bakery & Dessert", display_order=5),
        }
        session.add_all(cats.values())
        session.flush()

        # 3. 상품 목록 (현실적인 메뉴)
        products = [
            # Coffee
            Product(category_id=cats["coffee"].id, name="Americano", price=4500),
            Product(category_id=cats["coffee"].id, name="Cafe Latte", price=5000),
            Product(category_id=cats["coffee"].id, name="Vanilla Latte", price=5500),
            Product(category_id=cats["coffee"].id, name="Cappuccino", price=5000),
            Product(category_id=cats["coffee"].id, name="Caramel Macchiato", price=5800),
            Product(category_id=cats["coffee"].id, name="Cold Brew", price=5200),
            
            # Signature
            Product(category_id=cats["signature"].id, name="Sea Salt Cream Coffee", price=6500),
            Product(category_id=cats["signature"].id, name="Einspanner", price=6000),
            Product(category_id=cats["signature"].id, name="Cube Latte", price=6200),
            
            # Tea & Ade
            Product(category_id=cats["tea"].id, name="Earl Grey Tea", price=4800),
            Product(category_id=cats["tea"].id, name="Chamomile Tea", price=4800),
            Product(category_id=cats["tea"].id, name="Lemon Ade", price=5500),
            Product(category_id=cats["tea"].id, name="Grapefruit Ade", price=5800),
            Product(category_id=cats["tea"].id, name="Peach Iced Tea", price=5000),

            # Smoothie
            Product(category_id=cats["smoothie"].id, name="Strawberry Smoothie", price=6000),
            Product(category_id=cats["smoothie"].id, name="Mango Smoothie", price=6200),
            Product(category_id=cats["smoothie"].id, name="Yogurt Smoothie", price=5800),
            Product(category_id=cats["smoothie"].id, name="Java Chip Frappe", price=6500),
            Product(category_id=cats["smoothie"].id, name="Green Tea Frappe", price=6300),

            # Bakery
            Product(category_id=cats["bakery"].id, name="Cheese Cake", price=6500),
            Product(category_id=cats["bakery"].id, name="Tiramisu", price=7000),
            Product(category_id=cats["bakery"].id, name="Chocolate Mud Cake", price=6800),
            Product(category_id=cats["bakery"].id, name="Croffle (Plain)", price=3500),
            Product(category_id=cats["bakery"].id, name="Croffle (Cheese)", price=4200),
            Product(category_id=cats["bakery"].id, name="Bagel & Cream Cheese", price=4500),
        ]

        session.add_all(products)
        session.commit()
        print(f"[SUCCESS] Added {len(products)} menu items across 5 categories.")

    except Exception as e:
        session.rollback()
        print(f"[ERROR] {e}")
    finally:
        session.close()

if __name__ == "__main__":
    seed_rich_menu()