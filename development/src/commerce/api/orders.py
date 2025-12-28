import uuid
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from pydantic import BaseModel
from typing import List, Optional

from src.database.engine import get_db
from src.commerce.domain.models import Order, OrderItem, Payment, Product, OrderStatus
from src.commerce.auth.security import get_current_user
from src.commerce.services.webhook_sender import webhook_sender

router = APIRouter(prefix="/orders", tags=["Commerce: Orders"])

# =====================================================
# DTOs
# =====================================================

class OrderItemRequest(BaseModel):
    product_id: int
    quantity: int
    options: str = "{}"

class OrderCreate(BaseModel):
    store_id: int
    table_no: str
    items: List[OrderItemRequest]
    discount_amount: Optional[int] = 0
    discount_reason: Optional[str] = None

class OrderStatusUpdate(BaseModel):
    status: OrderStatus

class DiscountApply(BaseModel):
    discount_type: str  # "PERCENT" or "FIXED"
    discount_value: int  # 10 for 10%, or 1000 for 1000won
    reason: Optional[str] = None

class RefundRequest(BaseModel):
    reason: str
    partial_amount: Optional[int] = None  # None means full refund

# =====================================================
# Order Creation
# =====================================================

@router.post("/place")
def place_order(order_req: OrderCreate, db: Session = Depends(get_db)):
    """[POS] 주문 생성 (할인 적용 가능)"""
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

    # Apply discount
    final_amount = total_amount - (order_req.discount_amount or 0)
    if final_amount < 0:
        final_amount = 0

    order_id = str(uuid.uuid4())
    new_order = Order(
        id=order_id,
        store_id=order_req.store_id,
        table_no=order_req.table_no,
        total_amount=final_amount,
        status=OrderStatus.PENDING,
        items=db_items
    )

    db.add(new_order)
    db.commit()
    return {
        "order_id": order_id,
        "subtotal": total_amount,
        "discount": order_req.discount_amount or 0,
        "total_amount": final_amount,
        "status": "PENDING"
    }

# =====================================================
# Payment
# =====================================================

@router.post("/pay/{order_id}")
async def process_payment(
    order_id: str,
    pg_provider: str = "CASH",
    received_amount: int = 0,
    db: Session = Depends(get_db)
):
    """[결제] 결제 완료 처리"""
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.status == OrderStatus.PAID:
        raise HTTPException(status_code=400, detail="Order already paid")

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

    change = received_amount - order.total_amount if received_amount > 0 else 0

    # TgMain에 ORDER_PAID Webhook 발송
    await webhook_sender.send_order_paid(
        order_id=order_id,
        store_id=order.store_id,
        total_amount=order.total_amount,
        payment_method=pg_provider,
        items=[
            {"product_name": i.product_name, "quantity": i.quantity, "price": i.unit_price}
            for i in order.items
        ]
    )

    return {
        "status": "success",
        "receipt_id": payment.id,
        "amount": order.total_amount,
        "received": received_amount,
        "change": change
    }

# =====================================================
# Refund
# =====================================================

@router.post("/refund/{order_id}")
async def process_refund(
    order_id: str,
    req: RefundRequest,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """[환불] 주문 환불 처리"""
    if user["role"] not in ["owner", "admin"]:
        raise HTTPException(status_code=403, detail="Only owners can process refunds")

    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    payment = db.query(Payment).filter_by(order_id=order_id).first()
    if not payment:
        raise HTTPException(status_code=400, detail="No payment found for this order")

    if payment.status == "REFUNDED":
        raise HTTPException(status_code=400, detail="Already refunded")

    refund_amount = req.partial_amount if req.partial_amount else order.total_amount

    # Update payment status
    payment.status = "REFUNDED"
    order.status = OrderStatus.CANCELED

    # Create refund record (new payment with negative amount)
    refund_payment = Payment(
        id=f"ref_{uuid.uuid4().hex[:8]}",
        order_id=order_id,
        pg_provider=payment.pg_provider,
        amount=-refund_amount,
        status="REFUNDED"
    )
    db.add(refund_payment)
    db.commit()

    # TgMain에 ORDER_REFUNDED Webhook 발송
    await webhook_sender.send_order_refunded(
        order_id=order_id,
        store_id=order.store_id,
        refund_amount=refund_amount,
        reason=req.reason
    )

    return {
        "status": "refunded",
        "refund_id": refund_payment.id,
        "refund_amount": refund_amount,
        "reason": req.reason
    }

# =====================================================
# Order List & History
# =====================================================

@router.get("/list/{store_id}")
def get_active_orders(store_id: int, db: Session = Depends(get_db)):
    """[KDS] 현재 처리 중인 주문 목록"""
    orders = db.query(Order).filter(
        Order.store_id == store_id,
        Order.status.in_([OrderStatus.PAID, OrderStatus.PREPARING, OrderStatus.PENDING])
    ).order_by(desc(Order.created_at)).all()

    result = []
    for o in orders:
        result.append({
            "id": o.id,
            "table": o.table_no,
            "status": o.status,
            "total": o.total_amount,
            "time": o.created_at.strftime("%H:%M:%S"),
            "items": [{"name": i.product_name, "qty": i.quantity, "price": i.unit_price} for i in o.items]
        })
    return result

@router.get("/history/{store_id}")
def get_order_history(
    store_id: int,
    date: Optional[str] = None,  # YYYY-MM-DD format
    status: Optional[str] = None,
    limit: int = Query(default=50, le=200),
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """[주문내역] 주문 히스토리 조회 (검색/필터)"""
    query = db.query(Order).filter(Order.store_id == store_id)

    # Date filter
    if date:
        try:
            target_date = datetime.strptime(date, "%Y-%m-%d")
            next_date = target_date + timedelta(days=1)
            query = query.filter(and_(
                Order.created_at >= target_date,
                Order.created_at < next_date
            ))
        except ValueError:
            pass

    # Status filter
    if status:
        query = query.filter(Order.status == status)

    total_count = query.count()
    orders = query.order_by(desc(Order.created_at)).offset(offset).limit(limit).all()

    result = []
    for o in orders:
        payment = db.query(Payment).filter_by(order_id=o.id, status="PAID").first()
        result.append({
            "id": o.id,
            "table": o.table_no,
            "status": o.status,
            "total": o.total_amount,
            "payment_method": payment.pg_provider if payment else None,
            "created_at": o.created_at.isoformat(),
            "items": [{"name": i.product_name, "qty": i.quantity, "price": i.unit_price} for i in o.items]
        })

    return {
        "total": total_count,
        "orders": result
    }

@router.get("/{order_id}")
def get_order_detail(order_id: str, db: Session = Depends(get_db)):
    """[주문상세] 단일 주문 상세 조회"""
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    payment = db.query(Payment).filter_by(order_id=order_id).first()

    return {
        "id": order.id,
        "store_id": order.store_id,
        "table": order.table_no,
        "status": order.status,
        "total": order.total_amount,
        "created_at": order.created_at.isoformat(),
        "payment": {
            "id": payment.id,
            "method": payment.pg_provider,
            "amount": payment.amount,
            "status": payment.status,
            "paid_at": payment.paid_at.isoformat()
        } if payment else None,
        "items": [
            {
                "name": i.product_name,
                "qty": i.quantity,
                "price": i.unit_price,
                "subtotal": i.unit_price * i.quantity,
                "options": i.options
            }
            for i in order.items
        ]
    }

# =====================================================
# Order Status Update
# =====================================================

@router.put("/{order_id}/status")
def update_order_status(order_id: str, req: OrderStatusUpdate, db: Session = Depends(get_db)):
    """[KDS] 주문 상태 변경"""
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.status = req.status
    db.commit()
    return {"status": "success", "new_state": req.status}