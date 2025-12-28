from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, extract

from src.database.engine import get_db
from src.commerce.domain.models import Order, Payment, OrderItem, OrderStatus
from src.commerce.auth.security import get_current_user

router = APIRouter(prefix="/stats", tags=["Commerce: ERP & Analytics"])

# =====================================================
# Daily Sales
# =====================================================

@router.get("/sales/daily")
def get_daily_sales(
    store_id: int,
    days: int = 7,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """[ERP] 일별 매출 추이 보고서"""
    if str(user["store_id"]) != str(store_id) and user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Unauthorized")

    start_date = datetime.now() - timedelta(days=days)

    sales_data = db.query(
        func.date(Payment.paid_at).label("date"),
        func.sum(Payment.amount).label("total_revenue"),
        func.count(Payment.id).label("transaction_count")
    ).join(Order, Order.id == Payment.order_id).filter(
        Order.store_id == store_id,
        Payment.paid_at >= start_date,
        Payment.status == "PAID"
    ).group_by(
        func.date(Payment.paid_at)
    ).order_by(
        func.date(Payment.paid_at)
    ).all()

    return [
        {
            "date": str(row.date),
            "revenue": row.total_revenue or 0,
            "count": row.transaction_count
        }
        for row in sales_data
    ]


@router.get("/range")
def get_range_report(
    store_id: int,
    start_date: str,  # YYYY-MM-DD format
    end_date: str,    # YYYY-MM-DD format
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """[POS 리포트] 날짜 범위 매출 리포트"""
    if str(user["store_id"]) != str(store_id) and user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Unauthorized")

    try:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")

    end_next = end + timedelta(days=1)

    # Get all paid orders for the date range
    orders = db.query(Order).filter(
        Order.store_id == store_id,
        Order.created_at >= start,
        Order.created_at < end_next,
        Order.status.in_([OrderStatus.PAID, OrderStatus.COMPLETED])
    ).all()

    # Calculate metrics
    total_revenue = 0
    total_orders = len(orders)
    payment_methods = {}
    category_sales = {}
    hourly_sales = {str(h).zfill(2): {"count": 0, "revenue": 0} for h in range(24)}

    for order in orders:
        total_revenue += order.total_amount

        # Get payment info
        payment = db.query(Payment).filter_by(order_id=order.id, status="PAID").first()
        if payment:
            method = payment.pg_provider or "UNKNOWN"
            if method not in payment_methods:
                payment_methods[method] = {"count": 0, "revenue": 0}
            payment_methods[method]["count"] += 1
            payment_methods[method]["revenue"] += payment.amount

        # Hourly breakdown
        hour = order.created_at.strftime("%H")
        hourly_sales[hour]["count"] += 1
        hourly_sales[hour]["revenue"] += order.total_amount

        # Category breakdown (from order items)
        for item in order.items:
            cat_name = "기타"  # Default category
            if cat_name not in category_sales:
                category_sales[cat_name] = {"count": 0, "revenue": 0}
            category_sales[cat_name]["count"] += item.quantity
            category_sales[cat_name]["revenue"] += item.unit_price * item.quantity

    # Get refunds
    refunds = db.query(func.sum(Payment.amount)).join(Order).filter(
        Order.store_id == store_id,
        Payment.paid_at >= start,
        Payment.paid_at < end_next,
        Payment.status == "REFUNDED"
    ).scalar() or 0

    return {
        "start_date": str(start),
        "end_date": str(end),
        "total_revenue": total_revenue,
        "total_orders": total_orders,
        "average_order": total_revenue // total_orders if total_orders > 0 else 0,
        "refunds": abs(refunds),
        "net_revenue": total_revenue - abs(refunds),
        "payment_methods": payment_methods,
        "category_sales": category_sales,
        "hourly_sales": hourly_sales
    }


@router.get("/daily")
def get_daily_report(
    store_id: int,
    date: Optional[str] = None,  # YYYY-MM-DD format
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """[POS 일보] 특정 날짜의 상세 매출 리포트"""
    if str(user["store_id"]) != str(store_id) and user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Unauthorized")

    if date:
        try:
            target_date = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            target_date = datetime.now().date()
    else:
        target_date = datetime.now().date()

    next_date = target_date + timedelta(days=1)

    # Get all paid orders for the date
    orders = db.query(Order).filter(
        Order.store_id == store_id,
        Order.created_at >= target_date,
        Order.created_at < next_date,
        Order.status.in_([OrderStatus.PAID, OrderStatus.COMPLETED])
    ).all()

    # Calculate metrics
    total_revenue = 0
    total_orders = len(orders)
    payment_methods = {}
    hourly_sales = {str(h).zfill(2): {"count": 0, "revenue": 0} for h in range(24)}

    for order in orders:
        total_revenue += order.total_amount

        # Get payment info
        payment = db.query(Payment).filter_by(order_id=order.id, status="PAID").first()
        if payment:
            method = payment.pg_provider or "UNKNOWN"
            if method not in payment_methods:
                payment_methods[method] = {"count": 0, "revenue": 0}
            payment_methods[method]["count"] += 1
            payment_methods[method]["revenue"] += payment.amount

        # Hourly breakdown
        hour = order.created_at.strftime("%H")
        hourly_sales[hour]["count"] += 1
        hourly_sales[hour]["revenue"] += order.total_amount

    # Get refunds
    refunds = db.query(func.sum(Payment.amount)).join(Order).filter(
        Order.store_id == store_id,
        Payment.paid_at >= target_date,
        Payment.paid_at < next_date,
        Payment.status == "REFUNDED"
    ).scalar() or 0

    return {
        "date": str(target_date),
        "total_revenue": total_revenue,
        "total_orders": total_orders,
        "average_order": total_revenue // total_orders if total_orders > 0 else 0,
        "refunds": abs(refunds),
        "net_revenue": total_revenue - abs(refunds),
        "payment_methods": payment_methods,
        "hourly_sales": hourly_sales
    }


# =====================================================
# Product Rankings
# =====================================================

@router.get("/products/rank")
def get_product_ranking(
    store_id: int,
    limit: int = 10,
    days: int = 30,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """[ERP] 상품 판매 순위 (Best Sellers)"""
    start_date = datetime.now() - timedelta(days=days)

    ranking = db.query(
        OrderItem.product_name,
        func.sum(OrderItem.quantity).label("total_qty"),
        func.sum(OrderItem.unit_price * OrderItem.quantity).label("total_revenue")
    ).join(Order, Order.id == OrderItem.order_id).filter(
        Order.store_id == store_id,
        Order.status.in_([OrderStatus.PAID, OrderStatus.COMPLETED]),
        Order.created_at >= start_date
    ).group_by(
        OrderItem.product_name
    ).order_by(
        desc("total_qty")
    ).limit(limit).all()

    return [
        {
            "rank": idx + 1,
            "product_name": row.product_name,
            "sold_qty": row.total_qty,
            "revenue": row.total_revenue
        }
        for idx, row in enumerate(ranking)
    ]


# =====================================================
# Hourly Trend
# =====================================================

@router.get("/hourly")
def get_hourly_trend(
    store_id: int,
    date: Optional[str] = None,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """[분석] 시간대별 매출 추이"""
    if date:
        try:
            target_date = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            target_date = datetime.now().date()
    else:
        target_date = datetime.now().date()

    next_date = target_date + timedelta(days=1)

    orders = db.query(Order).filter(
        Order.store_id == store_id,
        Order.created_at >= target_date,
        Order.created_at < next_date,
        Order.status.in_([OrderStatus.PAID, OrderStatus.COMPLETED])
    ).all()

    hourly = {}
    for h in range(24):
        hourly[h] = {"hour": f"{h:02d}:00", "orders": 0, "revenue": 0}

    for order in orders:
        hour = order.created_at.hour
        hourly[hour]["orders"] += 1
        hourly[hour]["revenue"] += order.total_amount

    return list(hourly.values())


# =====================================================
# Dashboard Summary
# =====================================================

@router.get("/summary")
def get_dashboard_summary(
    store_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """[Dashboard] 실시간 매장 현황"""
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)

    # Today's revenue
    today_revenue = db.query(func.sum(Payment.amount)).join(Order).filter(
        Order.store_id == store_id,
        func.date(Payment.paid_at) == today,
        Payment.status == "PAID"
    ).scalar() or 0

    # Yesterday's revenue (for comparison)
    yesterday_revenue = db.query(func.sum(Payment.amount)).join(Order).filter(
        Order.store_id == store_id,
        func.date(Payment.paid_at) == yesterday,
        Payment.status == "PAID"
    ).scalar() or 0

    # Today's order count
    today_orders = db.query(func.count(Order.id)).filter(
        Order.store_id == store_id,
        func.date(Order.created_at) == today,
        Order.status.in_([OrderStatus.PAID, OrderStatus.COMPLETED])
    ).scalar() or 0

    # Pending orders
    pending_orders = db.query(func.count(Order.id)).filter(
        Order.store_id == store_id,
        Order.status.in_([OrderStatus.PENDING, OrderStatus.PREPARING])
    ).scalar() or 0

    # Growth rate
    growth = 0
    if yesterday_revenue > 0:
        growth = round((today_revenue - yesterday_revenue) / yesterday_revenue * 100, 1)

    return {
        "today_revenue": today_revenue,
        "yesterday_revenue": yesterday_revenue,
        "growth_rate": growth,
        "today_orders": today_orders,
        "pending_orders": pending_orders,
        "average_order": today_revenue // today_orders if today_orders > 0 else 0,
        "system_status": "ONLINE"
    }


# =====================================================
# Monthly Summary
# =====================================================

@router.get("/monthly")
def get_monthly_summary(
    store_id: int,
    year: Optional[int] = None,
    month: Optional[int] = None,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """[ERP] 월간 매출 요약"""
    if str(user["store_id"]) != str(store_id) and user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Unauthorized")

    now = datetime.now()
    year = year or now.year
    month = month or now.month

    # Get first and last day of month
    first_day = datetime(year, month, 1)
    if month == 12:
        last_day = datetime(year + 1, 1, 1)
    else:
        last_day = datetime(year, month + 1, 1)

    # Monthly totals
    monthly_data = db.query(
        func.sum(Payment.amount).label("total_revenue"),
        func.count(Payment.id).label("total_transactions")
    ).join(Order).filter(
        Order.store_id == store_id,
        Payment.paid_at >= first_day,
        Payment.paid_at < last_day,
        Payment.status == "PAID"
    ).first()

    # Weekly breakdown
    weeks = []
    current = first_day
    week_num = 1
    while current < last_day:
        week_end = min(current + timedelta(days=7), last_day)
        week_data = db.query(
            func.sum(Payment.amount).label("revenue"),
            func.count(Payment.id).label("count")
        ).join(Order).filter(
            Order.store_id == store_id,
            Payment.paid_at >= current,
            Payment.paid_at < week_end,
            Payment.status == "PAID"
        ).first()

        weeks.append({
            "week": week_num,
            "start": str(current.date()),
            "end": str((week_end - timedelta(days=1)).date()),
            "revenue": week_data.revenue or 0,
            "transactions": week_data.count or 0
        })

        current = week_end
        week_num += 1

    return {
        "year": year,
        "month": month,
        "total_revenue": monthly_data.total_revenue or 0,
        "total_transactions": monthly_data.total_transactions or 0,
        "average_per_transaction": (
            (monthly_data.total_revenue or 0) // (monthly_data.total_transactions or 1)
        ),
        "weeks": weeks
    }