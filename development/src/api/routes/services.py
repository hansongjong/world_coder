from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List

from src.database.engine import get_db
from src.database.models import ServiceCatalog
from src.api.schemas import ServiceCatalogCreate, ServiceCatalogResponse

router = APIRouter(prefix="/services", tags=["Service Catalog"])

@router.post("/", response_model=ServiceCatalogResponse, status_code=status.HTTP_201_CREATED)
def register_new_service(service: ServiceCatalogCreate, db: Session = Depends(get_db)):
    """
    [Admin] 새로운 서비스를 시스템 카탈로그에 등록합니다.
    """
    # 중복 체크
    existing = db.execute(select(ServiceCatalog).where(ServiceCatalog.service_code == service.service_code)).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Service code already exists")

    new_service = ServiceCatalog(
        service_code=service.service_code,
        service_name=service.service_name,
        description=service.description,
        base_price=service.base_price,
        config_schema=service.config_schema
    )
    db.add(new_service)
    db.commit()
    db.refresh(new_service)
    return new_service

@router.get("/", response_model=List[ServiceCatalogResponse])
def list_services(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    이용 가능한 모든 서비스 목록을 조회합니다.
    """
    stmt = select(ServiceCatalog).offset(skip).limit(limit)
    services = db.execute(stmt).scalars().all()
    return services