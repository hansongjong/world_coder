import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from src.database.engine import get_db
from src.database.models import Deployment, ServiceCatalog, User
from src.api.schemas import DeploymentCreate, DeploymentResponse

router = APIRouter(prefix="/deployments", tags=["Deployments"])

@router.post("/", response_model=DeploymentResponse, status_code=status.HTTP_201_CREATED)
def create_deployment(request: DeploymentCreate, db: Session = Depends(get_db)):
    """
    특정 서비스의 배포(실행)를 요청합니다.
    """
    # 1. 서비스 존재 확인
    service = db.get(ServiceCatalog, request.service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    # 2. 유저 존재 확인 (임시)
    user = db.get(User, request.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 3. 배포 정보 생성 (실제 Docker 배포 로직은 추후 Background Task로 연결)
    deployment_id = str(uuid.uuid4())
    
    new_deployment = Deployment(
        id=deployment_id,
        user_id=request.user_id,
        service_id=request.service_id,
        status="pending", # 초기 상태
        instance_config=request.instance_config,
        resource_id=None 
    )
    
    db.add(new_deployment)
    db.commit()
    db.refresh(new_deployment)
    
    return new_deployment

@router.get("/{deployment_id}", response_model=DeploymentResponse)
def get_deployment_status(deployment_id: str, db: Session = Depends(get_db)):
    """
    배포 상태를 조회합니다.
    """
    deployment = db.get(Deployment, deployment_id)
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")
    return deployment