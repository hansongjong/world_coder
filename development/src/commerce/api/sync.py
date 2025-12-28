"""
TgMain 연동 API - 외부 시스템과의 데이터 동기화
"""
import os
import hmac
import hashlib
import json
import logging
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Header, Request
from sqlalchemy.orm import Session

from src.database.engine import get_db
from src.commerce.domain.models import (
    ExpectedDelivery, ExpectedDeliveryItem, ExpectedDeliveryStatus,
    SyncLog, SyncDirection, Vendor, Product, Category
)
from src.commerce.auth.security import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/sync", tags=["External Sync"])


# =====================================================
# Pydantic Models
# =====================================================

class VendorInfo(BaseModel):
    vendor_id: int
    vendor_name: str
    vendor_phone: Optional[str] = None
    vendor_email: Optional[str] = None
    vendor_address: Optional[str] = None


class POItem(BaseModel):
    item_code: str
    item_name: str
    quantity: int
    unit: str = "EA"
    unit_price: float = 0


class PurchaseOrderData(BaseModel):
    po_number: str
    vendor: VendorInfo
    delivery_date: Optional[str] = None
    total_amount: int = 0
    items: List[POItem]
    notes: Optional[str] = None


class PurchaseOrderSync(BaseModel):
    source_system: str
    tenant_id: str
    target_store_id: int
    purchase_order: PurchaseOrderData
    idempotency_key: str


class VendorSync(BaseModel):
    source_system: str
    tenant_id: str
    target_store_id: int
    vendor: VendorInfo
    idempotency_key: str


class InventoryItemData(BaseModel):
    item_code: str
    item_name: str
    category_name: Optional[str] = None
    unit: str = "EA"
    unit_price: int = 0


class InventoryItemSync(BaseModel):
    source_system: str
    tenant_id: str
    target_store_id: int
    item: InventoryItemData
    idempotency_key: str


class SyncResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None


# =====================================================
# Signature Verification
# =====================================================

def verify_signature(
    api_key: str,
    signature: str,
    timestamp: str,
    body: bytes,
    secret_key: Optional[str] = None
) -> bool:
    """HMAC-SHA256 서명 검증"""
    secret = secret_key or os.getenv("WORLD_SECRET_KEY", "")
    expected_api_key = os.getenv("WORLD_API_KEY", "")

    if api_key != expected_api_key:
        return False

    body_hash = hashlib.sha256(body).hexdigest()
    message = f"POST\n/api/v1/sync\n{timestamp}\n{body_hash}"
    expected_signature = hmac.new(
        secret.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(signature, expected_signature)


def check_idempotency(db: Session, idempotency_key: str) -> Optional[SyncLog]:
    """Idempotency 체크 - 이미 처리된 요청인지 확인"""
    return db.query(SyncLog).filter(
        SyncLog.idempotency_key == idempotency_key,
        SyncLog.status == "SUCCESS"
    ).first()


def log_sync(
    db: Session,
    idempotency_key: str,
    direction: str,
    event_type: str,
    endpoint: str,
    payload: dict,
    status: str = "SUCCESS",
    response: Optional[dict] = None,
    error: Optional[str] = None
):
    """동기화 로그 기록"""
    sync_log = SyncLog(
        idempotency_key=idempotency_key,
        direction=direction,
        event_type=event_type,
        endpoint=endpoint,
        payload=json.dumps(payload, ensure_ascii=False),
        response=json.dumps(response, ensure_ascii=False) if response else None,
        status=status,
        error_message=error,
        processed_at=datetime.now() if status == "SUCCESS" else None
    )
    db.add(sync_log)
    db.commit()
    return sync_log


# =====================================================
# Inbound APIs (TgMain → World)
# =====================================================

@router.post("/purchase-order", response_model=SyncResponse)
async def receive_purchase_order(
    request: Request,
    req: PurchaseOrderSync,
    x_api_key: str = Header(None, alias="X-API-Key"),
    x_signature: str = Header(None, alias="X-Signature"),
    x_timestamp: str = Header(None, alias="X-Timestamp"),
    db: Session = Depends(get_db)
):
    """
    TgMain 발주서 수신 → 입고 예정 등록

    TgMain에서 발주 생성 시 World POS로 자동 전송되어
    매장에서 입고 예정 목록으로 확인 가능
    """
    # 1. Signature 검증 (프로덕션 환경에서 활성화)
    # body = await request.body()
    # if not verify_signature(x_api_key, x_signature, x_timestamp, body):
    #     raise HTTPException(status_code=401, detail="Invalid signature")

    # 2. Idempotency 체크
    existing = check_idempotency(db, req.idempotency_key)
    if existing:
        return SyncResponse(
            success=True,
            message="Already processed",
            data={"sync_log_id": existing.id}
        )

    try:
        po = req.purchase_order

        # 3. 입고 예정 생성
        expected_date = None
        if po.delivery_date:
            try:
                expected_date = datetime.strptime(po.delivery_date, "%Y-%m-%d")
            except ValueError:
                pass

        delivery = ExpectedDelivery(
            store_id=req.target_store_id,
            po_number=po.po_number,
            vendor_id=po.vendor.vendor_id,
            vendor_name=po.vendor.vendor_name,
            expected_date=expected_date,
            status=ExpectedDeliveryStatus.PENDING,
            total_amount=po.total_amount,
            notes=po.notes
        )
        db.add(delivery)
        db.flush()

        # 4. 품목 저장
        for item in po.items:
            delivery_item = ExpectedDeliveryItem(
                delivery_id=delivery.id,
                item_code=item.item_code,
                item_name=item.item_name,
                quantity=item.quantity,
                unit=item.unit,
                unit_price=int(item.unit_price)
            )
            db.add(delivery_item)

        db.commit()

        # 5. 로그 기록
        log_sync(
            db=db,
            idempotency_key=req.idempotency_key,
            direction=SyncDirection.INBOUND,
            event_type="PURCHASE_ORDER",
            endpoint="/api/v1/sync/purchase-order",
            payload=req.dict(),
            status="SUCCESS",
            response={"expected_delivery_id": delivery.id}
        )

        logger.info(f"Purchase order received: {po.po_number} → Delivery #{delivery.id}")

        return SyncResponse(
            success=True,
            message="Expected delivery registered",
            data={
                "expected_delivery_id": delivery.id,
                "po_number": po.po_number,
                "status": "PENDING"
            }
        )

    except Exception as e:
        db.rollback()
        logger.error(f"Purchase order sync failed: {str(e)}")

        log_sync(
            db=db,
            idempotency_key=req.idempotency_key,
            direction=SyncDirection.INBOUND,
            event_type="PURCHASE_ORDER",
            endpoint="/api/v1/sync/purchase-order",
            payload=req.dict(),
            status="FAILED",
            error=str(e)
        )

        raise HTTPException(status_code=500, detail=str(e))


@router.post("/vendor", response_model=SyncResponse)
async def sync_vendor(
    req: VendorSync,
    db: Session = Depends(get_db)
):
    """
    TgMain 거래처 정보 → World 공급사로 저장 (UPSERT)
    """
    existing = check_idempotency(db, req.idempotency_key)
    if existing:
        return SyncResponse(success=True, message="Already processed")

    try:
        vendor_data = req.vendor

        # UPSERT: external_id로 조회 후 있으면 업데이트, 없으면 생성
        vendor = db.query(Vendor).filter(
            Vendor.store_id == req.target_store_id,
            Vendor.external_id == vendor_data.vendor_id
        ).first()

        if vendor:
            # 업데이트
            vendor.name = vendor_data.vendor_name
            vendor.phone = vendor_data.vendor_phone
            vendor.email = vendor_data.vendor_email
            vendor.address = vendor_data.vendor_address
            vendor.updated_at = datetime.now()
            action = "updated"
        else:
            # 생성
            vendor = Vendor(
                store_id=req.target_store_id,
                external_id=vendor_data.vendor_id,
                name=vendor_data.vendor_name,
                phone=vendor_data.vendor_phone,
                email=vendor_data.vendor_email,
                address=vendor_data.vendor_address
            )
            db.add(vendor)
            action = "created"

        db.commit()

        log_sync(
            db=db,
            idempotency_key=req.idempotency_key,
            direction=SyncDirection.INBOUND,
            event_type="VENDOR_SYNC",
            endpoint="/api/v1/sync/vendor",
            payload=req.dict(),
            status="SUCCESS",
            response={"vendor_id": vendor.id, "action": action}
        )

        logger.info(f"Vendor {action}: {vendor_data.vendor_name} (ID: {vendor.id})")

        return SyncResponse(
            success=True,
            message=f"Vendor {action}",
            data={"vendor_id": vendor.id, "action": action}
        )

    except Exception as e:
        db.rollback()
        logger.error(f"Vendor sync failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/inventory-item", response_model=SyncResponse)
async def sync_inventory_item(
    req: InventoryItemSync,
    db: Session = Depends(get_db)
):
    """
    TgMain 품목 마스터 → World 상품으로 동기화 (UPSERT)
    """
    existing = check_idempotency(db, req.idempotency_key)
    if existing:
        return SyncResponse(success=True, message="Already processed")

    try:
        item_data = req.item

        # 카테고리 조회/생성
        category = None
        if item_data.category_name:
            category = db.query(Category).filter(
                Category.store_id == req.target_store_id,
                Category.name == item_data.category_name
            ).first()

            if not category:
                category = Category(
                    store_id=req.target_store_id,
                    name=item_data.category_name,
                    display_order=0
                )
                db.add(category)
                db.flush()

        # 상품 조회 (name으로 매칭 - item_code 필드가 없으면)
        product = db.query(Product).filter(
            Product.name == item_data.item_name,
            Product.category_id == (category.id if category else None)
        ).first()

        if product:
            product.price = item_data.unit_price
            action = "updated"
        else:
            product = Product(
                category_id=category.id if category else None,
                name=item_data.item_name,
                price=item_data.unit_price,
                description=f"[TgMain] {item_data.item_code}"
            )
            db.add(product)
            action = "created"

        db.commit()

        log_sync(
            db=db,
            idempotency_key=req.idempotency_key,
            direction=SyncDirection.INBOUND,
            event_type="INVENTORY_ITEM_SYNC",
            endpoint="/api/v1/sync/inventory-item",
            payload=req.dict(),
            status="SUCCESS",
            response={"product_id": product.id, "action": action}
        )

        logger.info(f"Product {action}: {item_data.item_name} (ID: {product.id})")

        return SyncResponse(
            success=True,
            message=f"Product {action}",
            data={"product_id": product.id, "action": action}
        )

    except Exception as e:
        db.rollback()
        logger.error(f"Inventory item sync failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================
# Expected Deliveries Management
# =====================================================

@router.get("/deliveries")
def list_expected_deliveries(
    store_id: int,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """입고 예정 목록 조회"""
    if str(user["store_id"]) != str(store_id) and user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Unauthorized")

    query = db.query(ExpectedDelivery).filter(ExpectedDelivery.store_id == store_id)

    if status:
        query = query.filter(ExpectedDelivery.status == status)

    deliveries = query.order_by(ExpectedDelivery.expected_date.desc()).all()

    return [
        {
            "id": d.id,
            "po_number": d.po_number,
            "vendor_name": d.vendor_name,
            "expected_date": str(d.expected_date) if d.expected_date else None,
            "status": d.status,
            "total_amount": d.total_amount,
            "item_count": len(d.items),
            "created_at": str(d.created_at)
        }
        for d in deliveries
    ]


@router.get("/deliveries/{delivery_id}")
def get_expected_delivery(
    delivery_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """입고 예정 상세 조회"""
    delivery = db.query(ExpectedDelivery).filter(ExpectedDelivery.id == delivery_id).first()

    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")

    if str(user["store_id"]) != str(delivery.store_id) and user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Unauthorized")

    return {
        "id": delivery.id,
        "po_number": delivery.po_number,
        "vendor_name": delivery.vendor_name,
        "expected_date": str(delivery.expected_date) if delivery.expected_date else None,
        "status": delivery.status,
        "total_amount": delivery.total_amount,
        "notes": delivery.notes,
        "items": [
            {
                "id": item.id,
                "item_code": item.item_code,
                "item_name": item.item_name,
                "quantity": item.quantity,
                "unit": item.unit,
                "unit_price": item.unit_price,
                "received_qty": item.received_qty
            }
            for item in delivery.items
        ],
        "created_at": str(delivery.created_at),
        "received_at": str(delivery.received_at) if delivery.received_at else None
    }


@router.post("/deliveries/{delivery_id}/receive")
async def confirm_delivery_received(
    delivery_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """입고 확인 처리"""
    from src.commerce.services.webhook_sender import webhook_sender

    delivery = db.query(ExpectedDelivery).filter(ExpectedDelivery.id == delivery_id).first()

    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")

    if str(user["store_id"]) != str(delivery.store_id) and user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Unauthorized")

    if delivery.status == ExpectedDeliveryStatus.RECEIVED:
        raise HTTPException(status_code=400, detail="Already received")

    # 상태 업데이트
    delivery.status = ExpectedDeliveryStatus.RECEIVED
    delivery.received_at = datetime.now()

    # 품목 수량 업데이트
    for item in delivery.items:
        item.received_qty = item.quantity

    db.commit()

    # TgMain에 입고 완료 이벤트 발송
    await webhook_sender.send_delivery_received(
        store_id=delivery.store_id,
        po_number=delivery.po_number,
        vendor_name=delivery.vendor_name,
        items=[
            {"item_code": i.item_code, "item_name": i.item_name, "quantity": i.received_qty}
            for i in delivery.items
        ],
        received_by=user.get("username")
    )

    logger.info(f"Delivery received: {delivery.po_number}")

    return {
        "success": True,
        "message": "Delivery confirmed",
        "delivery_id": delivery.id,
        "received_at": str(delivery.received_at)
    }


# =====================================================
# Sync Logs
# =====================================================

@router.get("/logs")
def list_sync_logs(
    direction: Optional[str] = None,
    event_type: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """동기화 로그 조회 (관리자용)"""
    if user["role"] not in ["admin", "owner"]:
        raise HTTPException(status_code=403, detail="Admin access required")

    query = db.query(SyncLog)

    if direction:
        query = query.filter(SyncLog.direction == direction)
    if event_type:
        query = query.filter(SyncLog.event_type == event_type)

    logs = query.order_by(SyncLog.created_at.desc()).limit(limit).all()

    return [
        {
            "id": log.id,
            "idempotency_key": log.idempotency_key,
            "direction": log.direction,
            "event_type": log.event_type,
            "status": log.status,
            "retry_count": log.retry_count,
            "error_message": log.error_message,
            "created_at": str(log.created_at),
            "processed_at": str(log.processed_at) if log.processed_at else None
        }
        for log in logs
    ]
