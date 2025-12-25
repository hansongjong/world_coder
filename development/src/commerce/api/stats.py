from datetime import datetime, timedelta
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from src.database.engine import get_db
from src.commerce.domain.models import Order, Payment, OrderItem, OrderStatus
from src.commerce.auth.security import get_current_user

router = APIRouter(prefix="/stats", tags=["Commerce: ERP & Analytics"])

@router.get("/sales/daily")
def get_daily_sales(
    store_id: int, 
    days: int = 7, 
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """
    [ERP] 일별 매출 추이 보고서
    """
    # 권한 체크
    if str(user["store_id"]) != str(store_id) and user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Unauthorized")

    start_date = datetime.now() - timedelta(days=days)
    
    # SQLite/MySQL 호환을 위해 날짜 캐스팅 주의 (여기서는 SQLite 기준 func.date 사용)
    # 결제 완료된 건만 집계
    sales_data = db.query(
        func.date(Payment.paid_at).label("date"),
        func.sum(Payment.amount).label("total_revenue"),
        func.count(Payment.id).label("transaction_count")
    ).filter(
        Payment.paid_at >= start_date,
        Payment.status == "PAID"
    ).group_by(
        func.date(Payment.paid_at)
    ).order_by(
        func.date(Payment.paid_at)
    ).all()
    
    return [
        {
            "date": row.date,
            "revenue": row.total_revenue or 0,
            "count": row.transaction_count
        }
        for row in sales_data
    ]

@router.get("/products/rank")
def get_product_ranking(
    store_id: int,
    limit: int = 5,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """
    [ERP] 상품 판매 순위 (Best Sellers)
    """
    # 해당 매장의 주문 아이템만 필터링하기 위해 Join 필요
    ranking = db.query(
        OrderItem.product_name,
        func.sum(OrderItem.quantity).label("total_qty"),
        func.sum(OrderItem.unit_price * OrderItem.quantity).label("total_revenue")
    ).join(Order, Order.id == OrderItem.order_id).filter(
        Order.store_id == store_id,
        Order.status == OrderStatus.PAID
    ).group_by(
        OrderItem.product_name
    ).order_by(
        desc("total_qty")
    ).limit(limit).all()
    
    return [
        {
            "product_name": row.product_name,
            "sold_qty": row.total_qty,
            "revenue": row.total_revenue
        }
        for row in ranking
    ]

@router.get("/summary")
def get_dashboard_summary(
    store_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """
    [Dashboard] 실시간 매장 현황 (오늘 매출, 대기 주문 등)
    """
    today = datetime.now().date()
    
    # 1. 오늘 매출
    today_revenue = db.query(func.sum(Payment.amount)).filter(
        func.date(Payment.paid_at) == today,
        Payment.status == "PAID"
    ).scalar() or 0
    
    # 2. 처리 대기 중인 주문 (주방)
    pending_orders = db.query(func.count(Order.id)).filter(
        Order.store_id == store_id,
        Order.status.in_([OrderStatus.PENDING, OrderStatus.PREPARING])
    ).scalar() or 0
    
    return {
        "today_revenue": today_revenue,
        "pending_orders": pending_orders,
        "system_status": "ONLINE"
    }