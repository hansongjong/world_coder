from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

class AccountStatus(str, Enum):
    ACTIVE = "active"
    BANNED = "banned"
    LIMITED = "limited" # 스팸 제재
    INVALID = "invalid"

class TgAccount(BaseModel):
    """텔레그램 계정 정보 (세션 관리용)"""
    phone_number: str = Field(..., description="International format ex) +8210...")
    api_id: Optional[int] = None
    api_hash: Optional[str] = None
    session_file: str  # .session 파일명
    status: AccountStatus = AccountStatus.ACTIVE
    last_used: datetime = Field(default_factory=datetime.now)

class TargetUser(BaseModel):
    """메시지 수신 대상 (유저 또는 그룹)"""
    user_id: Optional[int] = None
    username: Optional[str] = None
    phone: Optional[str] = None
    access_hash: Optional[int] = None # Telethon 사용 시 필요할 수 있음

class SendTask(BaseModel):
    """전송 작업 정의"""
    task_id: str
    account_phone: str # 어떤 계정으로 보낼지
    target: TargetUser
    message_text: str
    attachment_path: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)