import uuid
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from src.database.engine import get_db
from src.commerce.domain.models_phase2 import Reservation, ReservationStatus
from src.commerce.auth.security import get_current_user

router = APIRouter(prefix="/booking", tags=["Commerce: Booking"])

class BookingRequest(BaseModel):
    store_id: int
    guest_name: str
    guest_phone: str
    guest_count: int
    reserved_at: datetime
    duration_min: int = 60 # 기본 1시간

@router.post("/reserve")
def create_reservation(req: BookingRequest, db: Session = Depends(get_db)):
    """
    [예약 엔진] 시간 중복 체크 및 예약 생성
    """
    end_at = req.reserved_at + timedelta(minutes=req.duration_min)
    
    # 1. 중복 예약 체크 (단순화된 로직: 해당 매장의 같은 시간에 예약이 있는지 확인)
    # 실제로는 '테이블/룸' 리소스 관리가 필요하지만 Phase 2 초기엔 매장 단위로 처리
    conflict = db.query(Reservation).filter(
        Reservation.store_id == req.store_id,
        Reservation.status.in_([ReservationStatus.CONFIRMED, ReservationStatus.PENDING]),
        Reservation.reserved_at < end_at,
        Reservation.end_at > req.reserved_at
    ).first()
    
    if conflict:
        raise HTTPException(status_code=409, detail="Time slot already booked.")
    
    # 2. 예약 생성
    res_id = str(uuid.uuid4())
    reservation = Reservation(
        id=res_id,
        store_id=req.store_id,
        guest_name=req.guest_name,
        guest_phone=req.guest_phone,
        guest_count=req.guest_count,
        reserved_at=req.reserved_at,
        end_at=end_at,
        status=ReservationStatus.CONFIRMED, # 데모용으로 즉시 확정 (PG 연동 시 PENDING)
        deposit_amount=10000 # 노쇼 방지 보증금 예시
    )
    
    db.add(reservation)
    db.commit()
    
    # 3. 알림 발송 (Mock)
    # 실제로는 여기서 TG_SENDER_V1 함수를 호출하여 텔레그램 알림을 보냄
    print(f"[ALIMTALK] Reservation Confirmed for {req.guest_name} at {req.reserved_at}")
    
    return {"reservation_id": res_id, "status": "CONFIRMED", "message": "Reservation successful"}

@router.get("/list/{store_id}")
def get_reservations(store_id: int, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    """매장 예약 현황 조회 (직원/점주 전용)"""
    if str(user["store_id"]) != str(store_id) and user["role"] != "admin":
         raise HTTPException(status_code=403, detail="Unauthorized")
         
    return db.query(Reservation).filter_by(store_id=store_id).order_by(Reservation.reserved_at).all()