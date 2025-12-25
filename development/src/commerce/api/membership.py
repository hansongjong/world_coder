from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from src.database.engine import get_db
from src.commerce.domain.models_gap_v2 import MemberPoint, PointHistory

router = APIRouter(prefix="/membership", tags=["Commerce: Loyalty & Points"])

class PointRequest(BaseModel):
    store_id: int
    user_phone: str
    amount: int # 적립할 금액 (결제금액의 N%)

@router.post("/earn")
def earn_points(req: PointRequest, db: Session = Depends(get_db)):
    """[Loyalty] 포인트 적립"""
    member = db.query(MemberPoint).filter_by(store_id=req.store_id, user_phone=req.user_phone).first()
    
    if not member:
        member = MemberPoint(
            store_id=req.store_id,
            user_phone=req.user_phone,
            current_points=0,
            total_accumulated=0
        )
        db.add(member)
        db.flush() # ID 생성
        
    # 포인트 계산 (예: 결제액의 3% 적립 로직은 프론트/비즈니스 단에서 처리해서 amount로 넘김)
    points_to_add = int(req.amount * 0.03) # 간이 로직: 3%
    
    member.current_points += points_to_add
    member.total_accumulated += points_to_add
    member.last_visit = datetime.now()
    
    history = PointHistory(
        member_id=member.id,
        amount=points_to_add,
        reason="ORDER_REWARD",
        created_at=datetime.now()
    )
    db.add(history)
    db.commit()
    
    return {"phone": req.user_phone, "earned": points_to_add, "total": member.current_points}

@router.get("/check/{store_id}/{phone}")
def check_points(store_id: int, phone: str, db: Session = Depends(get_db)):
    """[Loyalty] 잔여 포인트 조회"""
    member = db.query(MemberPoint).filter_by(store_id=store_id, user_phone=phone).first()
    if not member:
        return {"exists": False, "points": 0}
    return {"exists": True, "points": member.current_points, "last_visit": member.last_visit}