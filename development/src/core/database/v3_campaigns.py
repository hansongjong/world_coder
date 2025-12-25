from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, JSON, Text
from src.core.database.v3_schema import V3ModelBase

class Campaign(V3ModelBase):
    __tablename__ = 'campaigns'
    
    campaign_id = Column(String(50), primary_key=True)
    user_id = Column(String(50), ForeignKey('master_users.user_id'))
    
    name = Column(String(100))
    status = Column(String(20), default="DRAFT") # DRAFT, SCHEDULED, RUNNING, PAUSED, COMPLETED, FAILED
    
    # 연결된 자원
    target_list_id = Column(String(50), ForeignKey('target_lists.list_id'))
    
    # 캠페인 설정 (메시지 내용, 딜레이, 세션 분배 전략 등)
    config = Column(JSON) 
    # 예: {"message": "Hi", "delay_min": 5, "delay_max": 10, "sessions_tag": "marketing_group_1"}
    
    # 스케줄링
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    start_time = Column(DateTime(timezone=True), nullable=True)
    end_time = Column(DateTime(timezone=True), nullable=True)
    
    # 통계
    total_targets = Column(Integer, default=0)
    sent_count = Column(Integer, default=0)
    fail_count = Column(Integer, default=0)