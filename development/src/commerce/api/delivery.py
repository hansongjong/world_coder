import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from src.database.engine import get_db
from src.commerce.domain.models_gap_v2 import DeliveryCall
from src.commerce.domain.models import Order

router = APIRouter(prefix="/delivery", tags=["Commerce: Delivery (TG-Linker)"])

class DeliveryRequest(BaseModel):
    order_id: str
    dest_address: str

@router.post("/call")
def call_rider(req: DeliveryRequest, db: Session = Depends(get_db)):
    """[TG-Linker] 배달 기사 호출"""
    # 주문 확인
    order = db.get(Order, req.order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # 배달 건 생성
    call_id = str(uuid.uuid4())
    delivery = DeliveryCall(
        id=call_id,
        order_id=req.order_id,
        dest_address=req.dest_address,
        status="REQUESTED",
        requested_at=datetime.now(),
        delivery_fee=3500 # 기본요금
    )
    db.add(delivery)
    db.commit()
    
    return {"status": "success", "call_id": call_id, "message": "Rider requested"}

@router.patch("/status/{call_id}")
def update_delivery_status(call_id: str, status: str, rider_name: str = None, db: Session = Depends(get_db)):
    """[Webhook] 라이더 배차/픽업/완료 상태 업데이트"""
    delivery = db.get(DeliveryCall, call_id)
    if not delivery:
        raise HTTPException(status_code=404, detail="Call not found")
        
    delivery.status = status
    if rider_name:
        delivery.rider_name = rider_name
    if status == "DELIVERED":
        delivery.delivered_at = datetime.now()
        
    db.commit()
    return {"status": "updated", "current_state": status}