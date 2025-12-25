from enum import Enum
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

class ChannelType(str, Enum):
    """지원하는 전송 채널 타입"""
    EMAIL = "email"
    SMS = "sms"
    SLACK = "slack"

class ContentType(str, Enum):
    """메시지 콘텐츠 타입"""
    TEXT = "text/plain"
    HTML = "text/html"

class Recipient(BaseModel):
    """수신자 정보"""
    name: Optional[str] = None
    email: EmailStr
    phone: Optional[str] = None

class MessageRequest(BaseModel):
    """
    전송 요청 엔티티 (DTO)
    Guide_for_Sending의 요청 명세를 반영합니다.
    """
    request_id: str = Field(..., description="Unique ID for tracking")
    channel: ChannelType = Field(default=ChannelType.EMAIL, description="sending channel")
    sender: Optional[str] = None
    recipients: List[Recipient]
    subject: str = Field(..., min_length=1, max_length=255)
    body: str
    content_type: ContentType = ContentType.HTML
    metadata: Dict[str, Any] = Field(default_factory=dict)

class SendResult(BaseModel):
    """전송 결과 엔티티"""
    success: bool
    request_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    message: str = "Sent successfully"
    error_code: Optional[str] = None