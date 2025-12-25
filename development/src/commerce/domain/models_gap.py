from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Boolean, Text, Float
from sqlalchemy.orm import relationship
from src.core.database.v3_schema import Base

# --- 1. 대기열 (Waiting Service) ---
class WaitingTicket(Base):
    __tablename__ = 'com_waiting_tickets'
    
    id = Column(String(50), primary_key=True) # UUID
    store_id = Column(Integer, ForeignKey('com_stores.id'))
    
    phone_number = Column(String(20))
    head_count = Column(Integer)
    
    queue_number = Column(Integer) # 대기 번호 (1, 2, 3...)
    status = Column(String(20), default="WAITING") # WAITING, CALLED, ENTERED, CANCELED
    
    created_at = Column(DateTime(timezone=True))
    called_at = Column(DateTime(timezone=True), nullable=True)

# --- 2. 만족도 조사 (CRM/Survey) ---
class CustomerSurvey(Base):
    __tablename__ = 'com_customer_surveys'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    store_id = Column(Integer, ForeignKey('com_stores.id'))
    order_id = Column(String(50), ForeignKey('com_orders.id'), nullable=True) # 어떤 주문에 대한 평가인가
    
    rating = Column(Float) # 1.0 ~ 5.0
    comment = Column(Text, nullable=True)
    tags = Column(String(255), nullable=True) # "친절해요,맛있어요" (CSV 형태)
    
    created_at = Column(DateTime(timezone=True))

# --- 3. 근태 관리 (HR/Attendance) ---
class AttendanceLog(Base):
    __tablename__ = 'com_hr_attendance'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    store_id = Column(Integer, ForeignKey('com_stores.id'))
    user_id = Column(Integer, ForeignKey('com_users.id')) # 직원 ID
    
    clock_in = Column(DateTime(timezone=True))  # 출근 시간
    clock_out = Column(DateTime(timezone=True), nullable=True) # 퇴근 시간
    
    work_hours = Column(Float, default=0.0) # 근무 시간 (시간 단위)
    status = Column(String(20), default="WORKING") # WORKING, FINISHED
    note = Column(String(100), nullable=True) # 지각 사유 등