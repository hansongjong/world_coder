from sqlalchemy.orm import Session
from src.core.database.v3_schema import MasterUser, Subscription, AuditLog
from datetime import datetime

class ERPService:
    def __init__(self, db: Session):
        self.db = db

    def check_billing_eligibility(self, user_id: str, service_cost: int) -> bool:
        """
        [ERP] 실행 전 과금 가능 여부 확인
        (구독 상태 확인 및 잔액 조회)
        """
        user = self.db.query(MasterUser).filter_by(user_id=user_id).first()
        if not user:
            return False
            
        # 간단한 로직: ENTERPRISE 티어는 무제한, 그 외는 포인트 체크 로직 필요
        # 여기서는 데모를 위해 Subscription이 ACTIVE 상태면 통과
        active_sub = self.db.query(Subscription).filter_by(
            user_id=user_id, status="ACTIVE"
        ).first()
        
        if not active_sub and user.tier_level != "ENTERPRISE":
            return False
            
        return True

    def process_billing(self, user_id: str, service_code: str, amount: int):
        """
        [ERP] 실행 후 실제 과금 처리
        """
        # 실제 구현 시: Transaction 테이블에 기록하고 User Balance 차감
        pass

class LegalAuditService:
    def __init__(self, db: Session):
        self.db = db

    def log_action(self, req_id: str, actor_id: str, action_type: str, details: str, ip_addr: str = None):
        """
        [Legal] 법적 증빙을 위한 불변 로그 기록
        """
        audit = AuditLog(
            req_id=req_id,
            actor_id=actor_id,
            action=action_type,
            snapshot_data=details,
            ip_address=ip_addr or "127.0.0.1"
        )
        self.db.add(audit)
        self.db.commit()