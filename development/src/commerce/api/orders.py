# 기존 파일 내용에 이어서 추가 (Append)
# 주의: 이 코드는 파일 전체를 덮어쓰는 것이 아니라, 기존 파일의 하단에 추가되는 것으로 간주합니다.
# 하지만 여기서는 편의상 Router에 추가하는 함수만 작성하므로, 
# 실제로는 기존 파일에 이 함수를 붙여넣거나 파일을 다시 작성해야 합니다.
# 안전을 위해 전체 파일을 다시 작성합니다.

import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pydantic import BaseModel
from typing import List

from src.database.engine import get_db
from src.commerce.domain.models import Order, OrderItem, Payment, Product, OrderStatus

router = APIRouter(prefix="/orders", tags=["Commerce: Orders"])

class OrderItemRequest(BaseModel):
    product_id: int
    quantity: int
    options: str = "{}"

class OrderCreate(BaseModel):
    store_id: int
    table_no: str
    items: List[OrderItemRequest]

class OrderStatusUpdate(BaseModel):
    status: OrderStatus

@router.post("/place")
def place_order(order_req: OrderCreate, db: Session = Depends(get_db)):
    """[POS] 주문 생성"""
    total_amount = 0
    db_items = []
    
    for item in order_req.items:
        product = db.get(Product, item.product_id)
        if not product or product.is_soldout:
            raise HTTPException(status_code=400, detail=f"Product {item.product_id} error")
        
        line_total = product.price * item.quantity
        total_amount += line_total
        
        db_items.append(OrderItem(
            product_name=product.name,
            unit_price=product.price,
            quantity=item.quantity,
            options=item.options
        ))
        
    order_id = str(uuid.uuid4())
    new_order = Order(
        id=order_id,
        store_id=order_req.store_id,
        table_no=order_req.table_no,
        total_amount=total_amount,
        status=OrderStatus.PENDING,
        items=db_items
    )
    
    db.add(new_order)
    db.commit()
    return {"order_id": order_id, "total_amount": total_amount, "status": "PENDING"}

@router.post("/pay/{order_id}")
def process_payment(order_id: str, pg_provider: str, db: Session = Depends(get_db)):
    """[결제] 결제 완료 처리"""
    order = db.get(Order, order_id)
    if not order: raise HTTPException(status_code=404, detail="Order not found")
    
    payment = Payment(
        id=f"pay_{uuid.uuid4().hex[:8]}",
        order_id=order_id,
        pg_provider=pg_provider,
        amount=order.total_amount,
        status="PAID"
    )
    order.status = OrderStatus.PAID
    db.add(payment)
    db.commit()
    return {"status": "success", "receipt_id": payment.id}

@router.get("/list/{store_id}")
def get_active_orders(store_id: int, db: Session = Depends(get_db)):
    """[KDS] 현재 처리 중인 주문 목록 (완료된 것 제외)"""
    orders = db.query(Order).filter(
        Order.store_id == store_id,
        Order.status.in_([OrderStatus.PAID, OrderStatus.PREPARING, OrderStatus.PENDING])
    ).order_by(desc(Order.created_at)).all()
    
    # KDS용 데이터 포맷팅
    result = []
    for o in orders:
        result.append({
            "id": o.id,
            "table": o.table_no,
            "status": o.status,
            "time": o.created_at.strftime("%H:%M:%S"),
            "items": [{"name": i.product_name, "qty": i.quantity} for i in o.items]
        })
    return result

@router.put("/{order_id}/status")
def update_order_status(order_id: str, req: OrderStatusUpdate, db: Session = Depends(get_db)):
    """[KDS] 주문 상태 변경 (조리중 -> 완료)"""
    order = db.get(Order, order_id)
    if not order: raise HTTPException(status_code=404, detail="Order not found")
    
    order.status = req.status
    db.commit()
    return {"status": "success", "new_state": req.status}