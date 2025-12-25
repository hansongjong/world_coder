from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from src.database.engine import get_db
from src.core.database.v3_schema import MasterUser, ExecutionRequest, AuditLog
from src.core.database.v3_extensions import TgSession
from src.core.database.v3_campaigns import Campaign

router = APIRouter(prefix="/dashboard", tags=["Visual Dashboard"])

@router.get("/summary")
def get_system_summary(db: Session = Depends(get_db)):
    """
    [Visual] 대시보드 상단 요약 카드 데이터
    - 총 유저 수, 활성 세션 수, 금일 실행 건수, 시스템 상태
    """
    today = datetime.now().date()
    
    total_users = db.query(MasterUser).count()
    active_sessions = db.query(TgSession).filter(TgSession.status == "ACTIVE").count()
    
    today_executions = db.query(ExecutionRequest).filter(
        func.date(ExecutionRequest.created_at) == today
    ).count()
    
    running_campaigns = db.query(Campaign).filter(Campaign.status == "RUNNING").count()
    
    return {
        "users": total_users,
        "sessions": {"active": active_sessions, "total": db.query(TgSession).count()},
        "executions_today": today_executions,
        "campaigns_running": running_campaigns,
        "system_status": "OPERATIONAL"
    }

@router.get("/chart/executions")
def get_execution_chart_data(days: int = 7, db: Session = Depends(get_db)):
    """
    [Visual] 최근 7일간 실행 및 성공/실패 추이 (차트용)
    """
    start_date = datetime.now() - timedelta(days=days)
    
    # 날짜별 통계 쿼리
    stats = db.query(
        func.date(ExecutionRequest.created_at).label("date"),
        ExecutionRequest.status,
        func.count(ExecutionRequest.req_id).label("count")
    ).filter(
        ExecutionRequest.created_at >= start_date
    ).group_by(
        func.date(ExecutionRequest.created_at),
        ExecutionRequest.status
    ).all()
    
    # 데이터 가공 (프론트엔드 차트 라이브러리 친화적 포맷)
    chart_data = {}
    for date, status, count in stats:
        date_str = str(date)
        if date_str not in chart_data:
            chart_data[date_str] = {"COMPLETED": 0, "FAILED": 0, "TOTAL": 0}
        
        if status in chart_data[date_str]:
            chart_data[date_str][status] += count
        chart_data[date_str]["TOTAL"] += count
        
    return chart_data

@router.get("/logs/recent")
def get_recent_audit_logs(limit: int = 10, db: Session = Depends(get_db)):
    """
    [Visual] 실시간 감사 로그 피드
    """
    logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit).all()
    return [
        {
            "time": log.created_at,
            "user": log.actor_id,
            "action": log.action,
            "details": log.snapshot_data
        }
        for log in logs
    ]