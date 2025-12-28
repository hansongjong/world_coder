"""
Multi-Business Test Data Seeding Script
========================================
업종별 테스트 데이터 시딩 (Cafe, Restaurant, Gym, Retail)

각 업종별로:
- Store (매장)
- Owner (점주 계정)
- StoreConfig (모듈 설정)
- Categories & Products (업종별 메뉴)
- Orders (주문 내역)

실행 방법:
  cd d:\python_projects\world_coder\development
  set PYTHONPATH=%CD%
  python scripts/seed_full_test.py

테스트 계정:
  - cafe / 1234    (Store ID: 1)
  - restaurant / 1234 (Store ID: 2)
  - gym / 1234     (Store ID: 3)
  - retail / 1234  (Store ID: 4)
"""
import sys
import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from src.core.database.v3_schema import Base
from src.commerce.domain.models import (
    Store, Product, Category, Order, OrderItem, Payment,
    OrderStatus, CommerceUser, UserRole, StoreConfig, UserStoreAccess
)
from src.commerce.domain.models_phase2 import Reservation, IoTDevice
from src.commerce.auth.security import get_password_hash
from src.core.config import settings

engine = create_engine(
    settings.DB_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DB_URL else {}
)
Base.metadata.create_all(bind=engine)
print("[*] Database tables created/verified.")


# ============================================================
# Business Type Definitions
# ============================================================
BUSINESS_TYPES = {
    "cafe": {
        "name": "TG Coffee Gangnam",
        "address": "Seoul, Gangnam-gu",
        "biz_number": "123-45-00001",
        "username": "cafe",
        "config": {
            "mod_payment": True,
            "mod_queue": True,
            "mod_reservation": False,
            "mod_inventory": True,
            "mod_crm": False,
            "mod_delivery": False,
            "mod_iot": False,
            "mod_subscription": False,
            "mod_invoice": False,
            "ui_mode": "KIOSK_LITE",
            "table_count": 8,
        },
        "categories": {
            "coffee": "Coffee",
            "signature": "Signature",
            "tea": "Tea & Ade",
            "bakery": "Bakery",
        },
        "products": {
            "coffee": [
                ("Americano", 4500),
                ("Cafe Latte", 5000),
                ("Vanilla Latte", 5500),
                ("Cappuccino", 5000),
                ("Caramel Macchiato", 5800),
                ("Cold Brew", 5200),
            ],
            "signature": [
                ("Sea Salt Cream Coffee", 6500),
                ("Einspanner", 6000),
                ("Cube Latte", 6200),
            ],
            "tea": [
                ("Earl Grey Tea", 4800),
                ("Lemon Ade", 5500),
                ("Grapefruit Ade", 5800),
                ("Peach Iced Tea", 5000),
            ],
            "bakery": [
                ("Cheese Cake", 6500),
                ("Tiramisu", 7000),
                ("Croffle", 3500),
                ("Bagel & Cream Cheese", 4500),
            ],
        },
    },
    "restaurant": {
        "name": "TG Korean BBQ",
        "address": "Seoul, Mapo-gu",
        "biz_number": "123-45-00002",
        "username": "restaurant",
        "config": {
            "mod_payment": True,
            "mod_queue": True,
            "mod_reservation": True,
            "mod_inventory": True,
            "mod_crm": True,
            "mod_delivery": True,
            "mod_iot": False,
            "mod_subscription": False,
            "mod_invoice": False,
            "ui_mode": "FULL_POS",
            "table_count": 15,
        },
        "categories": {
            "meat": "Meat",
            "side": "Side Dishes",
            "soup": "Soup & Stew",
            "drink": "Drinks",
            "set": "Set Menu",
        },
        "products": {
            "meat": [
                ("Samgyupsal (200g)", 16000),
                ("Chadol Beef (150g)", 18000),
                ("Galbi (300g)", 28000),
                ("Beef Bulgogi (200g)", 19000),
                ("Spicy Pork (200g)", 14000),
            ],
            "side": [
                ("Steamed Egg", 3000),
                ("Cheese Corn", 5000),
                ("Kimchi Fried Rice", 6000),
                ("Cold Noodles", 7000),
            ],
            "soup": [
                ("Doenjang Jjigae", 8000),
                ("Kimchi Jjigae", 8000),
                ("Budae Jjigae (2p)", 22000),
            ],
            "drink": [
                ("Soju", 5000),
                ("Beer", 5000),
                ("Makgeolli", 8000),
                ("Soft Drink", 2000),
            ],
            "set": [
                ("BBQ Set A (2p)", 45000),
                ("BBQ Set B (3p)", 65000),
                ("Family Set (4p)", 89000),
            ],
        },
    },
    "gym": {
        "name": "TG Fitness Center",
        "address": "Seoul, Songpa-gu",
        "biz_number": "123-45-00003",
        "username": "gym",
        "config": {
            "mod_payment": True,
            "mod_queue": False,
            "mod_reservation": True,
            "mod_inventory": False,
            "mod_crm": True,
            "mod_delivery": False,
            "mod_iot": True,
            "mod_subscription": True,
            "mod_invoice": False,
            "ui_mode": "KIOSK_LITE",
            "table_count": 0,
        },
        "categories": {
            "membership": "Membership",
            "pt": "Personal Training",
            "locker": "Locker & Towel",
            "supplement": "Supplements",
        },
        "products": {
            "membership": [
                ("1 Month Pass", 80000),
                ("3 Month Pass", 210000),
                ("6 Month Pass", 390000),
                ("12 Month Pass", 700000),
                ("Day Pass", 15000),
            ],
            "pt": [
                ("PT 10 Sessions", 500000),
                ("PT 20 Sessions", 900000),
                ("PT 30 Sessions", 1200000),
                ("Pilates 10 Sessions", 600000),
            ],
            "locker": [
                ("Locker 1 Month", 20000),
                ("Locker 3 Month", 50000),
                ("Towel Service 1 Month", 15000),
                ("Clothes Rental 1 Month", 30000),
            ],
            "supplement": [
                ("Protein Shake", 5000),
                ("BCAA", 3000),
                ("Energy Bar", 2500),
                ("Sports Drink", 2000),
            ],
        },
    },
    "retail": {
        "name": "TG Convenience Store",
        "address": "Seoul, Jongno-gu",
        "biz_number": "123-45-00004",
        "username": "retail",
        "config": {
            "mod_payment": True,
            "mod_queue": False,
            "mod_reservation": False,
            "mod_inventory": True,
            "mod_crm": False,
            "mod_delivery": True,
            "mod_iot": False,
            "mod_subscription": False,
            "mod_invoice": True,
            "ui_mode": "FULL_POS",
            "table_count": 0,
        },
        "categories": {
            "snack": "Snacks",
            "drink": "Beverages",
            "instant": "Instant Food",
            "daily": "Daily Necessities",
        },
        "products": {
            "snack": [
                ("Potato Chips", 1800),
                ("Chocolate Bar", 1500),
                ("Cookies Pack", 2500),
                ("Candy", 1000),
                ("Ice Cream", 2000),
            ],
            "drink": [
                ("Mineral Water", 1000),
                ("Cola 500ml", 1800),
                ("Coffee Can", 1500),
                ("Energy Drink", 2500),
                ("Juice Pack", 1200),
            ],
            "instant": [
                ("Cup Ramen", 1500),
                ("Kimbap", 2500),
                ("Sandwich", 3000),
                ("Onigiri", 1500),
                ("Lunch Box", 4500),
            ],
            "daily": [
                ("Tissue Pack", 1500),
                ("Toothbrush", 2000),
                ("Hand Sanitizer", 3000),
                ("Umbrella", 7000),
                ("Phone Charger", 12000),
            ],
        },
    },
}


def seed_all():
    print("=" * 60)
    print("  Multi-Business Test Data Seeding")
    print("=" * 60)

    session = Session(engine)

    try:
        # Clear all existing data
        print("\n[0] Clearing existing data...")
        session.query(Payment).delete()
        session.query(OrderItem).delete()
        session.query(Order).delete()
        session.query(Product).delete()
        session.query(Category).delete()
        session.query(StoreConfig).delete()
        session.query(UserStoreAccess).delete()
        session.query(CommerceUser).delete()
        session.query(Store).delete()
        session.commit()
        print("    [OK] All data cleared")

        total_stores = 0
        total_products = 0
        total_orders = 0

        for biz_type, biz_data in BUSINESS_TYPES.items():
            print(f"\n{'='*60}")
            print(f"  Creating {biz_type.upper()} Store")
            print(f"{'='*60}")

            # 1. Create Store
            store = Store(
                name=biz_data["name"],
                address=biz_data["address"],
                biz_number=biz_data["biz_number"],
                biz_type=biz_type
            )
            session.add(store)
            session.flush()
            print(f"  [1] Store: {store.name} (ID: {store.id})")

            # 2. Create Owner + UserStoreAccess
            owner = CommerceUser(
                username=biz_data["username"],
                password_hash=get_password_hash("1234"),
            )
            session.add(owner)
            session.flush()  # Get owner.id

            # Link owner to store with OWNER role
            access = UserStoreAccess(
                user_id=owner.id,
                store_id=store.id,
                role=UserRole.OWNER
            )
            session.add(access)
            print(f"  [2] Owner: {biz_data['username']} / 1234 (user_id: {owner.id})")

            # 3. Create Config (biz_type is in Store, not StoreConfig)
            config = StoreConfig(
                store_id=store.id,
                **biz_data["config"]
            )
            session.add(config)
            print(f"  [3] Config: {biz_type} mode")

            # 4. Create Categories & Products
            categories = {}
            for cat_key, cat_name in biz_data["categories"].items():
                cat = Category(
                    store_id=store.id,
                    name=cat_name,
                    display_order=list(biz_data["categories"].keys()).index(cat_key) + 1
                )
                session.add(cat)
                session.flush()
                categories[cat_key] = cat

            product_count = 0
            for cat_key, products in biz_data["products"].items():
                for name, price in products:
                    prod = Product(
                        category_id=categories[cat_key].id,
                        name=name,
                        price=price
                    )
                    session.add(prod)
                    product_count += 1

            session.flush()
            print(f"  [4] Menu: {len(categories)} categories, {product_count} products")
            total_products += product_count

            # 5. Generate Orders (7 days for each store)
            prods = session.query(Product).filter(
                Product.category_id.in_([c.id for c in categories.values()])
            ).all()

            order_count = 0
            revenue = 0
            for day_offset in range(7):
                current_date = datetime.now() - timedelta(days=day_offset)
                daily_orders = random.randint(5, 15)

                for _ in range(daily_orders):
                    items_count = random.randint(1, 3)
                    order_items = []
                    total_amt = 0

                    selected_prods = random.choices(prods, k=items_count)
                    order_id = str(uuid.uuid4())

                    for p in selected_prods:
                        qty = random.randint(1, 2)
                        line_total = p.price * qty
                        total_amt += line_total

                        order_items.append(OrderItem(
                            order_id=order_id,
                            product_name=p.name,
                            unit_price=p.price,
                            quantity=qty,
                            options="{}"
                        ))

                    order_time = current_date.replace(
                        hour=random.randint(9, 21),
                        minute=random.randint(0, 59)
                    )

                    order = Order(
                        id=order_id,
                        store_id=store.id,
                        table_no=f"T-{random.randint(1, max(1, biz_data['config']['table_count']))}" if biz_data['config']['table_count'] > 0 else None,
                        total_amount=total_amt,
                        status=OrderStatus.PAID,
                        created_at=order_time
                    )
                    session.add(order)
                    session.add_all(order_items)

                    payment = Payment(
                        id=f"pay_{uuid.uuid4().hex[:10]}",
                        order_id=order_id,
                        pg_provider=random.choice(["card", "cash", "kakao"]),
                        amount=total_amt,
                        status="PAID",
                        paid_at=order_time
                    )
                    session.add(payment)

                    order_count += 1
                    revenue += total_amt

            session.commit()
            print(f"  [5] Orders: {order_count} orders, {revenue:,} won")
            total_stores += 1
            total_orders += order_count

        # Create multi-store owner (김사장 - owns cafe + restaurant)
        print(f"\n{'='*60}")
        print("  Creating Multi-Store Owner")
        print(f"{'='*60}")

        boss = CommerceUser(
            username="boss",
            password_hash=get_password_hash("1234"),
        )
        session.add(boss)
        session.flush()

        # Boss owns store 1 (cafe) and store 2 (restaurant)
        session.add(UserStoreAccess(user_id=boss.id, store_id=1, role=UserRole.OWNER))
        session.add(UserStoreAccess(user_id=boss.id, store_id=2, role=UserRole.OWNER))
        session.commit()
        print(f"  [OK] boss / 1234 → Stores: 1 (cafe), 2 (restaurant)")

        # Create staff for cafe
        staff1 = CommerceUser(username="staff1", password_hash=get_password_hash("1234"))
        staff2 = CommerceUser(username="staff2", password_hash=get_password_hash("1234"))
        session.add_all([staff1, staff2])
        session.flush()

        session.add(UserStoreAccess(user_id=staff1.id, store_id=1, role=UserRole.STAFF))
        session.add(UserStoreAccess(user_id=staff2.id, store_id=1, role=UserRole.STAFF))
        session.commit()
        print(f"  [OK] staff1, staff2 / 1234 → Store: 1 (cafe)")

        # Summary
        print("\n" + "=" * 60)
        print("  SEEDING COMPLETE!")
        print("=" * 60)
        print(f"\n  Total Stores: {total_stores}")
        print(f"  Total Products: {total_products}")
        print(f"  Total Orders: {total_orders}")
        print("\n  Test Accounts:")
        print("  +------------+----------+-------------------+")
        print("  | Username   | Password | Access            |")
        print("  +------------+----------+-------------------+")
        for biz_type, data in BUSINESS_TYPES.items():
            print(f"  | {data['username']:<10} | 1234     | {biz_type} (owner)    |")
        print("  +------------+----------+-------------------+")
        print("  | boss       | 1234     | cafe + restaurant |")
        print("  | staff1     | 1234     | cafe (staff)      |")
        print("  | staff2     | 1234     | cafe (staff)      |")
        print("  +------------+----------+-------------------+")
        print()

    except Exception as e:
        session.rollback()
        print(f"\n[ERROR] Seeding failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()


if __name__ == "__main__":
    seed_all()
