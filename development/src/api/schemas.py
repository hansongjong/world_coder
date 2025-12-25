from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

# --- Service Catalog Schemas ---
class ServiceCatalogBase(BaseModel):
    service_code: str = Field(..., description="Unique code for the service (e.g., TG_SENDER_V1)")
    service_name: str
    description: Optional[str] = None
    base_price: int = 0
    config_schema: Dict[str, Any] = Field(default_factory=dict, description="JSON schema for service configuration")

class ServiceCatalogCreate(ServiceCatalogBase):
    pass

class ServiceCatalogResponse(ServiceCatalogBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

# --- Deployment Schemas ---
class DeploymentCreate(BaseModel):
    service_id: int
    user_id: int # 실제 인증 시스템 도입 시 토큰에서 추출
    instance_config: Dict[str, Any] = Field(..., description="Configuration matching the service schema")

class DeploymentResponse(BaseModel):
    id: str
    status: str
    service_id: int
    user_id: int
    resource_id: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True