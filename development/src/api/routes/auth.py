from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.database.engine import get_db
from src.core.security import verify_password, create_access_token
from src.core.database.v3_schema import MasterUser

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/token")
def login_access_token(
    db: Session = Depends(get_db), 
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 호환 토큰 로그인 엔드포인트
    """
    user = db.query(MasterUser).filter(MasterUser.username == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
        
    access_token = create_access_token(subject=user.user_id)
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user_tier": user.tier_level
    }