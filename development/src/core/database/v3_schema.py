from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, JSON, Boolean, Text
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()

class V3ModelBase(Base):
    __abstract__ = True
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# [Master Identity]: 사용자 및 테넌트 관리 (Phase 1 핵심)
class MasterUser(V3ModelBase):
    __tablename__ = 'master_users'
    
    user_id = Column(String(50), primary_key=True) # UUID
    username = Column(String(100), index=True, unique=True)
    email = Column(String(255), unique=True)
    hashed_password = Column(String(255)) # 보안 필드 추가
    tier_level = Column(String(20), default="STARTER")
    is_active = Column(Boolean, default=True)
    
    subscriptions = relationship("Subscription", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="actor")

# [Service Catalog]
class FunctionCatalog(V3ModelBase):
    __tablename__ = 'function_catalog'
    
    function_code = Column(String(50), primary_key=True)
    function_name = Column(String(100))
    handler_path = Column(String(255))
    resource_spec = Column(JSON)
    is_active = Column(Boolean, default=True)

# [ERP & Billing]
class Subscription(V3ModelBase):
    __tablename__ = 'subscriptions'
    
    sub_id = Column(String(50), primary_key=True)
    user_id = Column(String(50), ForeignKey('master_users.user_id'))
    plan_type = Column(String(50))
    status = Column(String(20))
    
    user = relationship("MasterUser", back_populates="subscriptions")

# [Serverless Execution]
class ExecutionRequest(V3ModelBase):
    __tablename__ = 'execution_requests'
    
    req_id = Column(String(50), primary_key=True)
    function_code = Column(String(50), ForeignKey('function_catalog.function_code'))
    user_id = Column(String(50), ForeignKey('master_users.user_id'))
    
    input_payload = Column(JSON)
    status = Column(String(20), default="QUEUED")
    result_output = Column(JSON, nullable=True)
    execution_time_ms = Column(Integer, nullable=True)

# [Legal Audit]
class AuditLog(V3ModelBase):
    __tablename__ = 'audit_logs'
    
    log_id = Column(Integer, primary_key=True, autoincrement=True)
    req_id = Column(String(50), ForeignKey('execution_requests.req_id'), nullable=True)
    actor_id = Column(String(50), ForeignKey('master_users.user_id'))
    action = Column(String(50))
    ip_address = Column(String(45))
    snapshot_data = Column(Text)
    
    actor = relationship("MasterUser", back_populates="audit_logs")