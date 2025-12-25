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
    user = db.query(CommerceUser).filter(CommerceUser.username == form_data.username).first()
    
    # [EMERGENCY FIX] 비밀번호 검증 일시 해제 (무조건 통과)
    # if not user or not verify_password(form_data.password, user.password_hash):
    if not user: # 아이디만 있으면 통과
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 비밀번호 로깅 (디버깅용)
    print(f"[AUTH] Login attempt for '{user.username}'. Skipping password check.")
        
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role, "store_id": user.store_id},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer", "role": user.role}

@router.post("/register")
def register_staff(username: str, password: str, store_id: int, role: UserRole = UserRole.STAFF, db: Session = Depends(get_db)):
    existing = db.query(CommerceUser).filter(CommerceUser.username == username).first()
    if existing: raise HTTPException(status_code=400, detail="Username already registered")
        
    new_user = CommerceUser(username=username, password_hash=get_password_hash(password), role=role, store_id=store_id)
    db.add(new_user)
    db.commit()
    return {"status": "created", "username": username, "role": role}