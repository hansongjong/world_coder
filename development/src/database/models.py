from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Integer, DateTime, ForeignKey, Boolean, Text, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func

class Base(DeclarativeBase):
    pass

class TimeStampedModel(Base):
    __abstract__ = True
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

# ---------------------------------------------------------
# 1. Identity & Access (ERP 연동 고려)
# ---------------------------------------------------------
class User(TimeStampedModel):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    email: Mapped[Optional[str]] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(default=True)
    role: Mapped[str] = mapped_column(String(20), default="client")  # admin, manager, client
    
    # Relations
    deployments: Mapped[List["Deployment"]] = relationship(back_populates="owner")
    orders: Mapped[List["Order"]] = relationship(back_populates="user")

# ---------------------------------------------------------
# 2. Service Catalog (TG_Service_Deployment_Catalog)
# ---------------------------------------------------------
class ServiceCatalog(TimeStampedModel):
    __tablename__ = "service_catalog"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    service_code: Mapped[str] = mapped_column(String(50), unique=True) # 예: TG_SENDER_V1
    service_name: Mapped[str] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(Text)
    base_price: Mapped[int] = mapped_column(Integer, default=0)
    config_schema: Mapped[dict] = mapped_column(JSON) # 서비스 실행에 필요한 설정 스키마 (JSON)
    
    deployments: Mapped[List["Deployment"]] = relationship(back_populates="service")

# ---------------------------------------------------------
# 3. Deployment Mapper (실제 구동되는 서비스 인스턴스)
# ---------------------------------------------------------
class Deployment(TimeStampedModel):
    __tablename__ = "deployments"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True) # UUID
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    service_id: Mapped[int] = mapped_column(ForeignKey("service_catalog.id"))
    
    status: Mapped[str] = mapped_column(String(20), default="stopped") # running, stopped, error, deployed
    instance_config: Mapped[dict] = mapped_column(JSON) # 실제 적용된 설정 (API Key 등)
    resource_id: Mapped[Optional[str]] = mapped_column(String(100)) # Docker Container ID or Process ID
    
    owner: Mapped["User"] = relationship(back_populates="deployments")
    service: Mapped["ServiceCatalog"] = relationship(back_populates="deployments")
    logs: Mapped[List["SystemLog"]] = relationship(back_populates="deployment")

# ---------------------------------------------------------
# 4. ERP & Billing (TG_ERP_Architecture)
# ---------------------------------------------------------
class Order(TimeStampedModel):
    __tablename__ = "orders"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    total_amount: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(20), default="pending") # paid, pending, cancelled
    
    user: Mapped["User"] = relationship(back_populates="orders")

# ---------------------------------------------------------
# 5. Legal & Logging (TG_Legal_Process)
# ---------------------------------------------------------
class SystemLog(TimeStampedModel):
    __tablename__ = "system_logs"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    deployment_id: Mapped[Optional[str]] = mapped_column(ForeignKey("deployments.id"))
    level: Mapped[str] = mapped_column(String(10), default="INFO")
    action_type: Mapped[str] = mapped_column(String(50)) # 예: MSG_SENT, LOGIN_ATTEMPT
    message: Mapped[str] = mapped_column(Text)
    ip_address: Mapped[Optional[str]] = mapped_column(String(50)) # 법적 증빙용 IP 기록
    
    deployment: Mapped["Deployment"] = relationship(back_populates="logs")