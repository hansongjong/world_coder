from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from src.database.engine import get_db
from src.commerce.domain.models_gap import AttendanceLog
from src.commerce.auth.security import get_current_user

router = APIRouter(prefix="/hr", tags=["Commerce: HR & Attendance"])

@router.post("/clock-in")
def clock_in(db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    """[HR] 출근 체크"""
    # 이미 출근 중인지 확인
    active = db.query(AttendanceLog).filter(
        AttendanceLog.user_id == user["id"] if "id" in user else None, # JWT 로직에 id 추가 필요하나 여기선 store_id로 대체
        AttendanceLog.status == "WORKING"
    ).first()
    
    if active:
        raise HTTPException(status_code=400, detail="Already clocked in.")
        
    # user_id는 실제 구현 시 JWT payload에서 추출해야 함. 여기서는 데모를 위해 store_id의 첫 번째 직원으로 가정하거나 user 딕셔너리 확장 필요.
    # 편의상 auth.security.get_current_user가 id를 반환한다고 가정.
    
    log = AttendanceLog(
        store_id=user["store_id"],
        user_id=1, # Mock User ID (실제로는 user['id'])
        clock_in=datetime.now(),
        status="WORKING"
    )
    db.add(log)
    db.commit()
    return {"status": "success", "time": log.clock_in, "message": "출근 처리되었습니다."}

@router.post("/clock-out")
def clock_out(db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    """[HR] 퇴근 체크 및 근무시간 계산"""
    log = db.query(AttendanceLog).filter(
        AttendanceLog.store_id == user["store_id"],
        AttendanceLog.status == "WORKING"
    ).order_by(AttendanceLog.clock_in.desc()).first()
    
    if not log:
        raise HTTPException(status_code=400, detail="No active work session found.")
        
    now = datetime.now()
    duration = (now - log.clock_in).total_seconds() / 3600.0 # 시간 단위
    
    log.clock_out = now
    log.work_hours = round(duration, 2)
    log.status = "FINISHED"
    
    db.commit()
    return {"status": "success", "work_hours": log.work_hours, "message": "퇴근 처리되었습니다."}