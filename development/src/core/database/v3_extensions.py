from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from src.core.database.v3_schema import V3ModelBase

# [Resource]: 텔레그램 세션 자산
class TgSession(V3ModelBase):
    __tablename__ = 'tg_sessions'
    
    session_id = Column(String(50), primary_key=True) # phone number or unique uuid
    user_id = Column(String(50), ForeignKey('master_users.user_id')) # 소유자
    phone = Column(String(20), index=True)
    session_file_path = Column(String(255)) # 실제 .session 파일 경로
    
    # 상태 및 프록시
    status = Column(String(20), default="UNCHECKED") # ACTIVE, BANNED, LIMITED, UNCHECKED
    proxy_url = Column(String(255), nullable=True) # protocol://user:pass@ip:port
    
    # 메타 데이터
    username = Column(String(100), nullable=True)
    first_name = Column(String(100), nullable=True)
    last_check_time = Column(String(50), nullable=True)

# [Data]: 타겟 리스트 (DB 저장 또는 파일 포인터)
class TargetList(V3ModelBase):
    __tablename__ = 'target_lists'
    
    list_id = Column(String(50), primary_key=True)
    user_id = Column(String(50), ForeignKey('master_users.user_id'))
    name = Column(String(100))
    source_type = Column(String(20)) # UPLOAD, SCRAPED
    
    # 데이터 통계
    total_count = Column(Integer, default=0)
    valid_count = Column(Integer, default=0)
    
    # 실제 데이터는 JSON 또는 별도 파일로 관리 (성능 최적화)
    file_path = Column(String(255), nullable=True)
    preview_data = Column(JSON, nullable=True) # 상위 10개 미리보기