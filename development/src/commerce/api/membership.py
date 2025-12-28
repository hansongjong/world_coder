from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel

from src.database.engine import get_db
from src.commerce.domain.models_gap_v2 import MemberPoint, PointHistory
from src.commerce.services.webhook_sender import webhook_sender

router = APIRouter(prefix="/membership", tags=["Commerce: Loyalty & Points"])

class PointRequest(BaseModel):
    store_id: int
    user_phone: str
    amount: int # 적립할 금액 (결제금액의 N%)

@router.post("/earn")
async def earn_points(
    req: PointRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """[Loyalty] 포인트 적립"""
    member = db.query(MemberPoint).filter_by(store_id=req.store_id, user_phone=req.user_phone).first()
    is_new_member = False

    if not member:
        is_new_member = True
        member = MemberPoint(
            store_id=req.store_id,
            user_phone=req.user_phone,
            current_points=0,
            total_accumulated=0
        )
        db.add(member)
        db.flush()  # ID 생성

    # 포인트 계산 (예: 결제액의 3% 적립)
    points_to_add = int(req.amount * 0.03)

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

    # 신규 회원이면 TgMain에 MEMBER_CREATED Webhook 발송
    if is_new_member:
        background_tasks.add_task(
            webhook_sender.send_member_created,
            store_id=req.store_id,
            member_id=member.id,
            phone=req.user_phone,
            name=None
        )

    return {"phone": req.user_phone, "earned": points_to_add, "total": member.current_points}

@router.get("/check/{store_id}/{phone}")
def check_points(store_id: int, phone: str, db: Session = Depends(get_db)):
    """[Loyalty] 잔여 포인트 조회"""
    member = db.query(MemberPoint).filter_by(store_id=store_id, user_phone=phone).first()
    if not member:
        return {"exists": False, "points": 0}
    return {"exists": True, "points": member.current_points, "last_visit": member.last_visit}