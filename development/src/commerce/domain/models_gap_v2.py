from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Boolean, Text, Float
from sqlalchemy.orm import relationship
from src.core.database.v3_schema import Base

# --- 1. 배달 (Delivery / TG-Linker) ---
class DeliveryCall(Base):
    __tablename__ = 'com_deliveries'
    
    id = Column(String(50), primary_key=True) # UUID
    order_id = Column(String(50), ForeignKey('com_orders.id'))
    
    dest_address = Column(String(255))
    rider_name = Column(String(50), nullable=True)
    rider_phone = Column(String(20), nullable=True)
    
    status = Column(String(20), default="REQUESTED") # REQUESTED, ASSIGNED, PICKED_UP, DELIVERED
    
    requested_at = Column(DateTime(timezone=True))
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    
    delivery_fee = Column(Integer, default=3000)

# --- 2. 멤버십 (Membership / Loyalty) ---
class MemberPoint(Base):
    __tablename__ = 'com_member_points'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    store_id = Column(Integer, ForeignKey('com_stores.id'))
    user_phone = Column(String(20), index=True) # 비회원도 전화번호로 적립 가능
    
    current_points = Column(Integer, default=0)
    total_accumulated = Column(Integer, default=0)
    
    last_visit = Column(DateTime(timezone=True))

class PointHistory(Base):
    __tablename__ = 'com_point_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    member_id = Column(Integer, ForeignKey('com_member_points.id'))
    
    amount = Column(Integer) # +적립, -사용
    reason = Column(String(50)) # ORDER_REWARD, USE_POINT
    created_at = Column(DateTime(timezone=True))

# --- 3. 재고 관리 (Inventory / SCM) ---
class InventoryItem(Base):
    __tablename__ = 'com_inventory'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    store_id = Column(Integer, ForeignKey('com_stores.id'))
    product_id = Column(Integer, ForeignKey('com_products.id'), nullable=True) # 완제품 재고일 경우
    
    item_name = Column(String(100)) # "원두(kg)", "우유(L)"
    current_qty = Column(Float, default=0.0)
    safety_stock = Column(Float, default=10.0) # 안전 재고 (이 아래로 떨어지면 알림)
    unit = Column(String(10)) # kg, ea, L
    
    last_updated = Column(DateTime(timezone=True))