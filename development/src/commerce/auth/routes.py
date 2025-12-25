from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.database.engine import get_db
from src.commerce.domain.models import CommerceUser, UserRole
from src.commerce.auth.security import (
    verify_password, 
    create_access_token, 
    get_password_hash, 
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter(prefix="/auth", tags=["Commerce: Auth"])

@router.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    [POS/Kiosk] 직원/점주 로그인 -> JWT 토큰 발급
    """
    user = db.query(CommerceUser).filter(CommerceUser.username == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # 토큰에 권한(Role)과 매장ID(Store_ID)를 심어서 발급
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role, "store_id": user.store_id},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer", "role": user.role}

@router.post("/register")
def register_staff(
    username: str, 
    password: str, 
    store_id: int, 
    role: UserRole = UserRole.STAFF, 
    db: Session = Depends(get_db)
):
    """
    [Admin] 신규 직원 등록 (운영 편의용)
    """
    # 중복 확인
    existing = db.query(CommerceUser).filter(CommerceUser.username == username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already registered")
        
    new_user = CommerceUser(
        username=username,
        password_hash=get_password_hash(password),
        role=role,
        store_id=store_id
    )
    db.add(new_user)
    db.commit()
    
    return {"status": "created", "username": username, "role": role}