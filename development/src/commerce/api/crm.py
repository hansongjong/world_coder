from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import Optional

from src.database.engine import get_db
from src.commerce.domain.models_gap import CustomerSurvey

router = APIRouter(prefix="/crm", tags=["Commerce: CRM & Survey"])

class SurveySubmit(BaseModel):
    store_id: int
    order_id: Optional[str] = None
    rating: float
    comment: Optional[str] = None
    tags: Optional[str] = None

@router.post("/survey")
def submit_survey(req: SurveySubmit, db: Session = Depends(get_db)):
    """[CRM] 고객 만족도 제출"""
    survey = CustomerSurvey(
        store_id=req.store_id,
        order_id=req.order_id,
        rating=req.rating,
        comment=req.comment,
        tags=req.tags,
        created_at=datetime.now()
    )
    db.add(survey)
    db.commit()
    return {"status": "success", "message": "소중한 의견 감사합니다."}

@router.get("/stats/{store_id}")
def get_satisfaction_stats(store_id: int, db: Session = Depends(get_db)):
    """[CRM] 매장 평점 통계"""
    avg_rating = db.query(func.avg(CustomerSurvey.rating)).filter_by(store_id=store_id).scalar() or 0.0
    count = db.query(func.count(CustomerSurvey.id)).filter_by(store_id=store_id).scalar() or 0
    
    # 최근 리뷰 5개
    recent = db.query(CustomerSurvey).filter_by(store_id=store_id).order_by(CustomerSurvey.created_at.desc()).limit(5).all()
    
    return {
        "average_rating": round(avg_rating, 1),
        "total_reviews": count,
        "recent_reviews": [{"rating": r.rating, "comment": r.comment} for r in recent]
    }