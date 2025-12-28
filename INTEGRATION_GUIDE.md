# World Coder ↔ TgMain 연동 가이드

> **문서 버전**: 1.0
> **작성일**: 2025-12-28
> **대상**: World Coder 개발팀

---

## 1. 연동 개요

World Coder는 **서비스 중심 소규모 사업장 POS 시스템**으로, TgMain(중소제조업체 ERP)과 연동하여 **매출/매입 자동화**를 구현합니다.

### 연동 목적
- World POS 매출 → TgMain ERP 세금계산서 자동 생성
- TgMain 발주서 → World 입고 예정 자동 등록
- 재고 부족 시 TgMain에 자동 발주 요청

---

## 2. World Coder가 구현해야 할 항목

### 2.1 TgMain에 호출할 API (Outbound)

#### API 1: 매출 동기화
```
POST https://api.tgmain.io/api/v1/sync/sales
```

**호출 시점**: 주문 결제 완료 시 (`OrderStatus.PAID`)

**Request Body**:
```json
{
  "source_system": "world_pos",
  "store_id": 1,
  "tenant_id": "tenant_abc",
  "order_id": "ord_abc123",
  "order_date": "2025-12-28",
  "order_time": "10:30:00",
  "customer": {
    "phone": "010-1234-5678",
    "name": "홍길동"
  },
  "items": [
    {
      "product_code": "PRD001",
      "product_name": "아메리카노",
      "quantity": 2,
      "unit_price": 4500,
      "line_total": 9000
    }
  ],
  "subtotal": 45000,
  "discount_amount": 5000,
  "vat_amount": 4000,
  "total_amount": 44000,
  "payment": {
    "method": "CARD",
    "status": "PAID",
    "paid_at": "2025-12-28T10:30:00Z"
  },
  "idempotency_key": "idem_xyz789"
}
```

#### API 2: 재고 출고 동기화
```
POST https://api.tgmain.io/api/v1/sync/inventory/out
```

**호출 시점**: 주문 생성 시 (재고 차감)

**Request Body**:
```json
{
  "source_system": "world_pos",
  "store_id": 1,
  "tenant_id": "tenant_abc",
  "ref_order_id": "ord_abc123",
  "warehouse_id": 1,
  "items": [
    {
      "item_code": "RM00001",
      "item_name": "원두 (브라질)",
      "quantity": 50,
      "unit": "G"
    }
  ],
  "txn_date": "2025-12-28",
  "idempotency_key": "inv_out_xyz789"
}
```

#### API 3: 고객 동기화
```
POST https://api.tgmain.io/api/v1/sync/customer
```

**호출 시점**: 신규 멤버십 가입 시

---

### 2.2 TgMain으로부터 받을 API (Inbound)

World Coder가 **제공해야 할 엔드포인트**:

#### API 1: 발주서 수신
```python
# src/commerce/api/sync.py (신규 생성)

from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import hmac
import hashlib

router = APIRouter(prefix="/api/v1/sync", tags=["External Sync"])

class VendorInfo(BaseModel):
    vendor_id: int
    vendor_name: str
    vendor_phone: Optional[str] = None

class POItem(BaseModel):
    item_code: str
    item_name: str
    quantity: int
    unit: str
    unit_price: float

class PurchaseOrderSync(BaseModel):
    source_system: str
    tenant_id: str
    target_store_id: int
    purchase_order: dict
    idempotency_key: str

@router.post("/purchase-order")
def receive_purchase_order(
    req: PurchaseOrderSync,
    x_api_key: str = Header(...),
    x_signature: str = Header(...),
    x_timestamp: str = Header(...),
    db: Session = Depends(get_db)
):
    """
    TgMain 발주서 수신 → 입고 예정 등록
    """
    # 1. API Key & Signature 검증
    if not verify_signature(x_api_key, x_signature, x_timestamp, req):
        raise HTTPException(status_code=401, detail="Invalid signature")

    # 2. Idempotency 체크
    existing = check_idempotency(db, req.idempotency_key)
    if existing:
        return {"success": True, "message": "Already processed", "data": existing}

    # 3. 입고 예정 테이블에 저장
    po = req.purchase_order
    delivery = ExpectedDelivery(
        store_id=req.target_store_id,
        po_number=po["po_number"],
        vendor_name=po["vendor"]["vendor_name"],
        expected_date=po["delivery_date"],
        status="PENDING",
        total_amount=po["total_amount"]
    )
    db.add(delivery)

    # 4. 품목 저장
    for item in po["items"]:
        delivery_item = ExpectedDeliveryItem(
            delivery_id=delivery.id,
            item_code=item["item_code"],
            item_name=item["item_name"],
            quantity=item["quantity"],
            unit=item["unit"]
        )
        db.add(delivery_item)

    db.commit()

    return {
        "success": True,
        "message": "Expected delivery registered",
        "data": {
            "expected_delivery_id": delivery.id,
            "status": "PENDING"
        }
    }
```

#### API 2: 거래처 동기화
```python
@router.post("/vendor")
def sync_vendor(req: VendorSync, db: Session = Depends(get_db)):
    """TgMain 거래처 정보 → World 공급사로 저장"""
    # UPSERT 로직 구현
    pass

@router.post("/inventory-item")
def sync_inventory_item(req: ItemSync, db: Session = Depends(get_db)):
    """TgMain 품목 마스터 → World 상품으로 동기화"""
    # UPSERT 로직 구현
    pass
```

---

### 2.3 필요한 DB 테이블 추가

```python
# src/commerce/domain/models_sync.py (신규)

class ExpectedDelivery(Base):
    """입고 예정 (TgMain 발주서 수신)"""
    __tablename__ = "expected_deliveries"

    id = Column(Integer, primary_key=True)
    store_id = Column(Integer, nullable=False)
    po_number = Column(String(50), unique=True)  # TgMain 발주번호
    vendor_name = Column(String(100))
    expected_date = Column(Date)
    status = Column(String(20), default="PENDING")  # PENDING, RECEIVED, CANCELLED
    total_amount = Column(Integer)
    received_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)

class ExpectedDeliveryItem(Base):
    """입고 예정 품목"""
    __tablename__ = "expected_delivery_items"

    id = Column(Integer, primary_key=True)
    delivery_id = Column(Integer, ForeignKey("expected_deliveries.id"))
    item_code = Column(String(50))
    item_name = Column(String(100))
    quantity = Column(Integer)
    unit = Column(String(10))
    received_qty = Column(Integer, default=0)

class SyncLog(Base):
    """연동 로그 (Idempotency 포함)"""
    __tablename__ = "sync_logs"

    id = Column(Integer, primary_key=True)
    idempotency_key = Column(String(100), unique=True)
    direction = Column(String(10))  # IN, OUT
    event_type = Column(String(50))
    payload = Column(Text)
    status = Column(String(20))
    created_at = Column(DateTime, default=datetime.now)
```

---

### 2.4 Webhook 발송 구현

```python
# src/commerce/services/webhook_sender.py (신규)

import httpx
import hmac
import hashlib
from datetime import datetime
import json

class WebhookSender:
    def __init__(self, api_key: str, secret_key: str):
        self.api_key = api_key
        self.secret_key = secret_key
        self.base_url = "https://api.tgmain.io"

    def _generate_signature(self, method: str, path: str, timestamp: str, body: str) -> str:
        message = f"{method}\n{path}\n{timestamp}\n{hashlib.sha256(body.encode()).hexdigest()}"
        return hmac.new(
            self.secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()

    async def send_event(self, event_type: str, payload: dict):
        """Webhook 이벤트 발송"""
        timestamp = datetime.utcnow().isoformat() + "Z"

        webhook_data = {
            "webhook_id": f"wh_{uuid.uuid4().hex[:12]}",
            "event_type": event_type,
            "event_version": "1.0",
            "source": "world_pos",
            "timestamp": timestamp,
            "delivery_attempt": 1,
            "payload": payload
        }

        body = json.dumps(webhook_data)
        path = "/api/v1/webhooks/receive"
        signature = self._generate_signature("POST", path, timestamp, body)

        headers = {
            "Content-Type": "application/json",
            "X-API-Key": self.api_key,
            "X-Timestamp": timestamp,
            "X-Signature": signature
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}{path}",
                content=body,
                headers=headers,
                timeout=5.0
            )

            if response.status_code != 200:
                # 실패 시 재전송 큐에 등록
                await self._queue_retry(webhook_data)

            return response
```

---

### 2.5 orders.py 수정 (결제 완료 시 Webhook 발송)

```python
# src/commerce/api/orders.py 수정

from src.commerce.services.webhook_sender import WebhookSender

webhook = WebhookSender(
    api_key=os.getenv("TGMAIN_API_KEY"),
    secret_key=os.getenv("TGMAIN_SECRET_KEY")
)

@router.post("/pay/{order_id}")
async def process_payment(...):
    # 기존 결제 로직...

    # 결제 완료 후 TgMain에 Webhook 발송
    await webhook.send_event("ORDER_PAID", {
        "order_id": order_id,
        "store_id": order.store_id,
        "total_amount": order.total_amount,
        "payment_method": pg_provider,
        "items": [
            {"product_name": i.product_name, "quantity": i.quantity, "price": i.unit_price}
            for i in order.items
        ]
    })

    return {"status": "success", ...}
```

---

## 3. 인증 구현

### 헤더 구조
```
X-API-Key: wc_live_xxxxx
X-Timestamp: 2025-12-28T10:30:00Z
X-Signature: hmac_sha256_signature
```

### Signature 생성
```python
def generate_signature(secret_key, method, path, timestamp, body):
    body_hash = hashlib.sha256(body.encode()).hexdigest()
    message = f"{method}\n{path}\n{timestamp}\n{body_hash}"
    return hmac.new(secret_key.encode(), message.encode(), hashlib.sha256).hexdigest()
```

---

## 4. 에러 처리

### 표준 에러 응답
```json
{
  "success": false,
  "error": {
    "code": "ERR_VALIDATION_FAILED",
    "message": "Validation failed for field: store_id",
    "details": [{"field": "store_id", "reason": "required"}],
    "trace_id": "trc_abc123"
  }
}
```

### 에러 코드
| 코드 | 설명 |
|------|------|
| ERR_AUTHENTICATION_FAILED | API Key/Signature 오류 |
| ERR_DUPLICATE_REQUEST | 중복 요청 (idempotency_key) |
| ERR_VALIDATION_FAILED | 요청 데이터 검증 실패 |
| ERR_RESOURCE_NOT_FOUND | 리소스 없음 |

---

## 5. 환경변수 설정

```env
# .env 추가
TGMAIN_API_KEY=wc_live_xxxxxxxx
TGMAIN_SECRET_KEY=sk_xxxxxxxxxxxxxxxx
TGMAIN_BASE_URL=https://api.tgmain.io
TGMAIN_WEBHOOK_URL=https://api.tgmain.io/api/v1/webhooks/receive
```

---

## 6. 구현 체크리스트

- [ ] `/api/v1/sync/purchase-order` 엔드포인트 구현
- [ ] `/api/v1/sync/vendor` 엔드포인트 구현
- [ ] `/api/v1/sync/inventory-item` 엔드포인트 구현
- [ ] `expected_deliveries` 테이블 생성
- [ ] `sync_logs` 테이블 생성 (Idempotency)
- [ ] WebhookSender 클래스 구현
- [ ] 결제 완료 시 ORDER_PAID 이벤트 발송
- [ ] 재고 부족 시 STOCK_LOW 이벤트 발송
- [ ] 입고 확인 시 DELIVERY_RECEIVED 이벤트 발송
- [ ] HMAC Signature 검증 미들웨어 구현
- [ ] Webhook 재전송 큐 구현 (Redis 권장)

---

## 7. 참조 문서

- **연동 설계서**: `D:\python_projects\World_Planner\TG_MASTER_DESIGN\01_Visual_Dashboard\TG_Integration_Spec.html`
- **API 계약서**: `D:\python_projects\World_Planner\TG_MASTER_DESIGN\01_Visual_Dashboard\TG_API_Contract.html`

---

**문의**: TgMain 연동 관련 기술 문의는 api@tgmain.io로 연락하세요.
