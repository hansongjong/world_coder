from sqlalchemy import Column, String
from src.core.database.v3_schema import MasterUser

# 주의: 이 코드는 모델 정의 참고용입니다. 
# 실제로는 v3_schema.py의 MasterUser 클래스에 hashed_password 컬럼을 추가해야 합니다.

"""
[수정 가이드] src/core/database/v3_schema.py 파일을 열고 MasterUser 클래스를 아래와 같이 수정하십시오.

class MasterUser(V3ModelBase):
    __tablename__ = 'master_users'
    
    user_id = Column(String(50), primary_key=True)
    username = Column(String(100), index=True)
    email = Column(String(255), unique=True)
    hashed_password = Column(String(255), nullable=False) # <--- 추가됨
    tier_level = Column(String(20), default="STARTER")
    is_active = Column(Boolean, default=True) # <--- 추가됨
    
    ... (나머지 관계 설정)
"""