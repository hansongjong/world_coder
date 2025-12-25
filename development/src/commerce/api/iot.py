import uuid
import random
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from src.database.engine import get_db
from src.commerce.domain.models_phase2 import IoTDevice, DeviceType
from src.commerce.auth.security import get_current_user

router = APIRouter(prefix="/iot", tags=["Commerce: IoT Control"])

class DeviceRegister(BaseModel):
    store_id: int
    name: str
    device_type: DeviceType
    ip_address: str = "192.168.0.100"

class DeviceCommand(BaseModel):
    command: str # OPEN, CLOSE, RESTART, ON, OFF

@router.post("/device")
def register_device(req: DeviceRegister, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    """IoT 장비 등록 (점주 전용)"""
    if user["role"] not in ["owner", "admin"]:
        raise HTTPException(status_code=403, detail="Only Owners can register devices")
        
    dev_id = f"dev_{uuid.uuid4().hex[:8]}"
    device = IoTDevice(
        id=dev_id,
        store_id=req.store_id,
        name=req.name,
        device_type=req.device_type,
        ip_address=req.ip_address,
        status="ONLINE",
        last_heartbeat=datetime.now()
    )
    db.add(device)
    db.commit()
    return device

@router.post("/control/{device_id}")
def control_device(device_id: str, cmd: DeviceCommand, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    """
    [IoT 엔진] 장치 원격 제어
    실제 하드웨어 통신 대신 Mock Response를 반환합니다.
    """
    device = db.get(IoTDevice, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
        
    # 권한 체크
    if str(user["store_id"]) != str(device.store_id) and user["role"] != "admin":
         raise HTTPException(status_code=403, detail="Unauthorized access to device")

    # Command Execution Simulation
    success = random.choice([True, True, True, False]) # 25% 확률로 실패 시뮬레이션
    
    if success:
        # 상태 업데이트 로직 (가정)
        if cmd.command == "OPEN" and device.device_type == DeviceType.DOOR_LOCK:
            device.status = "UNLOCKED"
        elif cmd.command == "ON":
            device.status = "ACTIVE"
            
        db.commit()
        return {"status": "SUCCESS", "device": device.name, "executed_command": cmd.command}
    else:
        return {"status": "FAILED", "device": device.name, "error": "Device timeout or unreachable"}