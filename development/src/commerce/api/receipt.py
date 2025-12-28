"""
영수증 API - 영수증 조회 및 출력
"""
from datetime import datetime
from io import BytesIO
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional

from src.database.engine import get_db
from src.commerce.domain.models import Order, Payment, Store, OrderStatus

router = APIRouter(prefix="/receipt", tags=["Commerce: Receipt"])


# =====================================================
# Receipt Data
# =====================================================

@router.get("/{order_id}")
def get_receipt_data(order_id: str, db: Session = Depends(get_db)):
    """
    [영수증] 영수증 데이터 조회

    결제 완료된 주문의 영수증 데이터를 반환합니다.
    """
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.status not in [OrderStatus.PAID, OrderStatus.COMPLETED]:
        raise HTTPException(status_code=400, detail="Order not paid yet")

    payment = db.query(Payment).filter_by(order_id=order_id, status="PAID").first()
    if not payment:
        raise HTTPException(status_code=400, detail="Payment not found")

    store = db.get(Store, order.store_id)

    # 부가세 계산 (10%)
    vat = int(order.total_amount * 0.1 / 1.1)
    supply_amount = order.total_amount - vat

    return {
        "receipt_id": payment.id,
        "order_id": order.id,
        "store": {
            "name": store.name if store else "Unknown",
            "address": store.address if store else "",
            "biz_number": store.biz_number if store else ""
        },
        "order_info": {
            "table_no": order.table_no,
            "order_date": order.created_at.strftime("%Y-%m-%d"),
            "order_time": order.created_at.strftime("%H:%M:%S")
        },
        "items": [
            {
                "name": item.product_name,
                "qty": item.quantity,
                "unit_price": item.unit_price,
                "subtotal": item.unit_price * item.quantity
            }
            for item in order.items
        ],
        "payment": {
            "method": payment.pg_provider,
            "paid_at": payment.paid_at.strftime("%Y-%m-%d %H:%M:%S") if payment.paid_at else None,
            "supply_amount": supply_amount,
            "vat": vat,
            "total_amount": order.total_amount
        }
    }


@router.get("/{order_id}/text")
def get_receipt_text(order_id: str, db: Session = Depends(get_db)):
    """
    [영수증] 텍스트 형식 영수증 (ESC/POS 프린터용)

    열 프린터에서 바로 출력 가능한 텍스트 형식 영수증을 반환합니다.
    """
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.status not in [OrderStatus.PAID, OrderStatus.COMPLETED]:
        raise HTTPException(status_code=400, detail="Order not paid yet")

    payment = db.query(Payment).filter_by(order_id=order_id, status="PAID").first()
    if not payment:
        raise HTTPException(status_code=400, detail="Payment not found")

    store = db.get(Store, order.store_id)

    # 부가세 계산
    vat = int(order.total_amount * 0.1 / 1.1)
    supply_amount = order.total_amount - vat

    # 영수증 텍스트 생성 (32자 폭 기준)
    width = 32
    line = "=" * width
    dash = "-" * width

    lines = []
    lines.append(line)
    lines.append(center_text(store.name if store else "STORE", width))
    lines.append(center_text(store.address if store else "", width))
    if store and store.biz_number:
        lines.append(center_text(f"사업자번호: {store.biz_number}", width))
    lines.append(line)

    # 주문 정보
    lines.append(f"주문번호: {order.id[:8]}...")
    lines.append(f"테이블: {order.table_no or '-'}")
    lines.append(f"일시: {order.created_at.strftime('%Y-%m-%d %H:%M')}")
    lines.append(dash)

    # 품목
    lines.append(f"{'품목':<16}{'수량':>4}{'금액':>12}")
    lines.append(dash)
    for item in order.items:
        name = item.product_name[:14]
        qty = str(item.quantity)
        amount = format_number(item.unit_price * item.quantity)
        lines.append(f"{name:<16}{qty:>4}{amount:>12}")
    lines.append(dash)

    # 금액
    lines.append(f"{'공급가액':<20}{format_number(supply_amount):>12}")
    lines.append(f"{'부가세':<20}{format_number(vat):>12}")
    lines.append(line)
    lines.append(f"{'합계':<20}{format_number(order.total_amount):>12}")
    lines.append(line)

    # 결제
    method_name = get_payment_method_name(payment.pg_provider)
    lines.append(f"결제수단: {method_name}")
    if payment.paid_at:
        lines.append(f"결제시간: {payment.paid_at.strftime('%H:%M:%S')}")
    lines.append(line)

    # 푸터
    lines.append(center_text("감사합니다", width))
    lines.append(center_text("Thank you!", width))
    lines.append("")

    receipt_text = "\n".join(lines)

    return {
        "order_id": order_id,
        "receipt_text": receipt_text,
        "width": width
    }


@router.get("/{order_id}/html")
def get_receipt_html(order_id: str, db: Session = Depends(get_db)):
    """
    [영수증] HTML 형식 영수증 (웹/앱 표시용)
    """
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.status not in [OrderStatus.PAID, OrderStatus.COMPLETED]:
        raise HTTPException(status_code=400, detail="Order not paid yet")

    payment = db.query(Payment).filter_by(order_id=order_id, status="PAID").first()
    if not payment:
        raise HTTPException(status_code=400, detail="Payment not found")

    store = db.get(Store, order.store_id)

    # 부가세 계산
    vat = int(order.total_amount * 0.1 / 1.1)
    supply_amount = order.total_amount - vat

    # HTML 생성
    items_html = ""
    for item in order.items:
        subtotal = item.unit_price * item.quantity
        items_html += f"""
        <tr>
            <td>{item.product_name}</td>
            <td class="right">{item.quantity}</td>
            <td class="right">{item.unit_price:,}</td>
            <td class="right">{subtotal:,}</td>
        </tr>
        """

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>영수증 - {order.id[:8]}</title>
        <style>
            body {{ font-family: 'Noto Sans KR', sans-serif; max-width: 300px; margin: 0 auto; padding: 20px; }}
            .header {{ text-align: center; border-bottom: 2px solid #000; padding-bottom: 10px; }}
            .header h2 {{ margin: 0; }}
            .info {{ margin: 10px 0; font-size: 12px; }}
            table {{ width: 100%; border-collapse: collapse; font-size: 12px; }}
            th, td {{ padding: 5px; text-align: left; }}
            .right {{ text-align: right; }}
            .total-row {{ border-top: 2px solid #000; font-weight: bold; }}
            .footer {{ text-align: center; margin-top: 20px; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h2>{store.name if store else 'STORE'}</h2>
            <p>{store.address if store else ''}</p>
            <p>사업자번호: {store.biz_number if store else ''}</p>
        </div>

        <div class="info">
            <p>주문번호: {order.id[:8]}...</p>
            <p>테이블: {order.table_no or '-'}</p>
            <p>일시: {order.created_at.strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>

        <table>
            <thead>
                <tr>
                    <th>품목</th>
                    <th class="right">수량</th>
                    <th class="right">단가</th>
                    <th class="right">금액</th>
                </tr>
            </thead>
            <tbody>
                {items_html}
            </tbody>
        </table>

        <table style="margin-top: 10px;">
            <tr>
                <td>공급가액</td>
                <td class="right">{supply_amount:,}원</td>
            </tr>
            <tr>
                <td>부가세</td>
                <td class="right">{vat:,}원</td>
            </tr>
            <tr class="total-row">
                <td>합계</td>
                <td class="right">{order.total_amount:,}원</td>
            </tr>
        </table>

        <div class="info" style="margin-top: 10px;">
            <p>결제수단: {get_payment_method_name(payment.pg_provider)}</p>
            <p>결제시간: {payment.paid_at.strftime('%Y-%m-%d %H:%M:%S') if payment.paid_at else '-'}</p>
        </div>

        <div class="footer">
            <p>감사합니다</p>
            <p>Thank you!</p>
        </div>
    </body>
    </html>
    """

    return StreamingResponse(
        BytesIO(html.encode('utf-8')),
        media_type="text/html",
        headers={"Content-Disposition": f"inline; filename=receipt_{order_id[:8]}.html"}
    )


# =====================================================
# Helper Functions
# =====================================================

def center_text(text: str, width: int) -> str:
    """텍스트를 지정된 폭에 중앙 정렬"""
    if len(text) >= width:
        return text[:width]
    padding = (width - len(text)) // 2
    return " " * padding + text


def format_number(num: int) -> str:
    """숫자를 천 단위 콤마 포맷"""
    return f"{num:,}원"


def get_payment_method_name(method: str) -> str:
    """결제 수단 한글명"""
    methods = {
        "CASH": "현금",
        "CARD": "카드",
        "kakao": "카카오페이",
        "toss": "토스",
        "naver": "네이버페이",
        "samsung": "삼성페이",
        "apple": "애플페이"
    }
    return methods.get(method, method)
