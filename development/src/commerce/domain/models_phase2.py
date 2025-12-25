from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Boolean, Text, Enum
from sqlalchemy.orm import relationship
from src.core.database.v3_schema import Base
import enum

class ReservationStatus(str, enum.Enum):
    PENDING = "pending"     # 예약 신청 (보증금 대기)
    CONFIRMED = "confirmed" # 확정
    CANCELED = "canceled"   # 취소
    COMPLETED = "completed" # 이용 완료
    NOSHOW = "noshow"       # 노쇼

class Reservation(Base):
    __tablename__ = 'com_reservations'
    
    id = Column(String(50), primary_key=True) # UUID
    store_id = Column(Integer, ForeignKey('com_stores.id'))
    user_id = Column(Integer, ForeignKey('com_users.id'), nullable=True) # 비회원 예약 가능 시 Nullable
    
    guest_name = Column(String(50))
    guest_phone = Column(String(20))
    guest_count = Column(Integer, default=1)
    
    reserved_at = Column(DateTime(timezone=True)) # 예약 시간
    end_at = Column(DateTime(timezone=True))      # 종료 시간 (공간 대여 시 필요)
    
    status = Column(String(20), default=ReservationStatus.PENDING)
    deposit_amount = Column(Integer, default=0) # 노쇼 방지 보증금
    
    # 알림 발송 여부
    is_notified = Column(Boolean, default=False)

class DeviceType(str, enum.Enum):
    DOOR_LOCK = "door_lock"
    PRINTER = "printer"
    LIGHTING = "lighting"
    KIOSK = "kiosk"

class IoTDevice(Base):
    __tablename__ = 'com_iot_devices'
    
    id = Column(String(50), primary_key=True) # Device Serial or UUID
    store_id = Column(Integer, ForeignKey('com_stores.id'))
    name = Column(String(50)) # "정문 도어락", "2번룸 전등"
    device_type = Column(String(20))
    
    ip_address = Column(String(50), nullable=True)
    auth_token = Column(String(100), nullable=True) # 장치 접속 토큰
    status = Column(String(20), default="OFFLINE")
    
    last_heartbeat = Column(DateTime(timezone=True), nullable=True)