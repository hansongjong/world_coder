import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel

from src.database.engine import get_db
from src.commerce.domain.models_gap import WaitingTicket

router = APIRouter(prefix="/queue", tags=["Commerce: Waiting Service"])

class WaitingRegister(BaseModel):
    store_id: int
    phone_number: str
    head_count: int

@router.post("/register")
def register_waiting(req: WaitingRegister, db: Session = Depends(get_db)):
    """
    [대기] 웨이팅 등록 및 번호표 발급
    """
    # 1. 오늘 날짜의 마지막 번호 조회
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    last_ticket = db.query(WaitingTicket).filter(
        WaitingTicket.store_id == req.store_id,
        WaitingTicket.created_at >= today_start
    ).order_by(WaitingTicket.queue_number.desc()).first()
    
    next_num = (last_ticket.queue_number + 1) if last_ticket else 1
    
    # 2. 티켓 생성
    ticket = WaitingTicket(
        id=str(uuid.uuid4()),
        store_id=req.store_id,
        phone_number=req.phone_number,
        head_count=req.head_count,
        queue_number=next_num,
        status="WAITING",
        created_at=datetime.now()
    )
    db.add(ticket)
    db.commit()
    
    # 3. 내 앞 웨이팅 수 계산
    waiting_count = db.query(WaitingTicket).filter(
        WaitingTicket.store_id == req.store_id,
        WaitingTicket.status == "WAITING",
        WaitingTicket.queue_number < next_num
    ).count()
    
    return {
        "ticket_id": ticket.id,
        "queue_number": next_num,
        "ahead_teams": waiting_count,
        "message": f"대기 접수 완료. 고객님 번호는 {next_num}번 입니다."
    }

@router.get("/status/{store_id}")
def get_waiting_status(store_id: int, db: Session = Depends(get_db)):
    """현재 대기 현황 (전광판용)"""
    waiting_list = db.query(WaitingTicket).filter(
        WaitingTicket.store_id == store_id,
        WaitingTicket.status == "WAITING"
    ).order_by(WaitingTicket.queue_number).all()
    
    return {
        "total_waiting": len(waiting_list),
        "current_call": waiting_list[0].queue_number if waiting_list else None,
        "list": [{"num": t.queue_number, "phone": t.phone_number[-4:]} for t in waiting_list]
    }