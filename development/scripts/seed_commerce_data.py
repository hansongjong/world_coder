import sys
import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path

# 프로젝트 루트 경로 설정
sys.path.append(str(Path(__file__).resolve().parents[2]))

from sqlalchemy.orm import Session
from src.database.engine import engine
from src.commerce.domain.models import Store, Product, Category, Order, OrderItem, Payment, OrderStatus, CommerceUser, UserRole
from src.commerce.auth.security import get_password_hash

def seed_data():
    print("[*] Generating Mock Commerce Data for ERP Testing...")
    session = Session(engine)
    
    try:
        # 1. 매장 및 사용자 생성
        if not session.query(Store).first():
            store = Store(name="TG Coffee Gangnam", address="Seoul, Gangnam-gu", biz_number="123-45-67890")
            session.add(store)
            session.flush() # ID 확보
            
            owner = CommerceUser(
                username="owner", 
                password_hash=get_password_hash("1234"),
                role=UserRole.OWNER,
                store_id=store.id
            )
            session.add(owner)
            
            # 카테고리 & 상품
            cat_coffee = Category(store_id=store.id, name="Coffee")
            cat_dessert = Category(store_id=store.id, name="Dessert")
            session.add_all([cat_coffee, cat_dessert])
            session.flush()
            
            prods = [
                Product(category_id=cat_coffee.id, name="Americano", price=4500),
                Product(category_id=cat_coffee.id, name="Latte", price=5000),
                Product(category_id=cat_dessert.id, name="Cheese Cake", price=6500),
            ]
            session.add_all(prods)
            session.commit()
            print("    [+] Created Store, Owner, Menu.")
        else:
            store = session.query(Store).first()
            prods = session.query(Product).all()

        # 2. 과거 30일치 주문 데이터 생성
        print("    [+] Generating 30 days of sales history...")
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        total_orders = 0
        current_date = start_date
        
        while current_date <= end_date:
            # 하루에 5~15건의 주문 발생
            daily_orders = random.randint(5, 15)
            
            for _ in range(daily_orders):
                # 주문 생성
                items_count = random.randint(1, 4)
                order_items = []
                total_amt = 0
                
                # 아이템 랜덤 선택
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
                
                # 주문 객체
                # 시간을 해당 날짜의 랜덤 시간으로 설정
                order_time = current_date + timedelta(hours=random.randint(9, 20), minutes=random.randint(0, 59))
                
                order = Order(
                    id=order_id,
                    store_id=store.id,
                    table_no=f"T-{random.randint(1, 10)}",
                    total_amount=total_amt,
                    status=OrderStatus.PAID,
                    created_at=order_time
                )
                session.add(order)
                session.add_all(order_items)
                
                # 결제 객체
                payment = Payment(
                    id=f"pay_{uuid.uuid4().hex[:10]}",
                    order_id=order_id,
                    pg_provider="card",
                    amount=total_amt,
                    status="PAID",
                    paid_at=order_time # 주문과 동시 결제 가정
                )
                session.add(payment)
                
                total_orders += 1
            
            current_date += timedelta(days=1)
            
        session.commit()
        print(f"[SUCCESS] Generated {total_orders} historical orders.")
        
    except Exception as e:
        session.rollback()
        print(f"[ERROR] Seeding failed: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    seed_data()