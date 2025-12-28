from datetime import timedelta
from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.database.engine import get_db
from src.commerce.domain.models import CommerceUser, UserRole, UserStoreAccess, Store
from src.commerce.auth.security import (
    verify_password,
    create_access_token,
    get_password_hash,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter(prefix="/auth", tags=["Commerce: Auth"])


# --- Request/Response Models ---
class LoginRequest(BaseModel):
    username: str
    password: str


class StoreAccessInfo(BaseModel):
    store_id: int
    store_name: str
    biz_type: str
    role: str


class LoginResponse(BaseModel):
    user_id: int
    username: str
    stores: list[StoreAccessInfo]


class SelectStoreRequest(BaseModel):
    user_id: int
    store_id: int


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    username: str
    store_id: int
    store_name: str
    role: str


# --- Step 1: Login (verify user, return accessible stores) ---
@router.post("/login", response_model=LoginResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """
    1단계: 로그인 (유저 확인 + 접근 가능한 매장 목록 반환)
    """
    user = db.query(CommerceUser).filter(CommerceUser.username == req.username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    # TODO: 비밀번호 검증 활성화
    # if not verify_password(req.password, user.password_hash):
    #     raise HTTPException(status_code=401, detail="Invalid password")

    print(f"[AUTH] Login: {user.username} (id: {user.id})")

    # 유저가 접근 가능한 매장 목록
    accesses = db.query(UserStoreAccess).filter(UserStoreAccess.user_id == user.id).all()

    if not accesses:
        raise HTTPException(status_code=403, detail="No store access assigned")

    stores = []
    for access in accesses:
        store = db.query(Store).filter(Store.id == access.store_id).first()
        if store:
            stores.append(StoreAccessInfo(
                store_id=store.id,
                store_name=store.name,
                biz_type=store.biz_type,
                role=access.role
            ))

    return LoginResponse(
        user_id=user.id,
        username=user.username,
        stores=stores
    )


# --- Step 2: Select Store (issue JWT token) ---
@router.post("/select-store", response_model=TokenResponse)
def select_store(req: SelectStoreRequest, db: Session = Depends(get_db)):
    """
    2단계: 매장 선택 → JWT 토큰 발급
    """
    # 유저 확인
    user = db.query(CommerceUser).filter(CommerceUser.id == req.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 해당 매장 접근 권한 확인
    access = db.query(UserStoreAccess).filter(
        UserStoreAccess.user_id == req.user_id,
        UserStoreAccess.store_id == req.store_id
    ).first()

    if not access:
        raise HTTPException(status_code=403, detail="No access to this store")

    store = db.query(Store).filter(Store.id == req.store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")

    print(f"[AUTH] Store selected: {user.username} → {store.name} (role: {access.role})")

    # JWT 토큰 발급
    access_token = create_access_token(
        data={
            "sub": user.username,
            "user_id": user.id,
            "store_id": store.id,
            "role": access.role,
        },
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=user.id,
        username=user.username,
        store_id=store.id,
        store_name=store.name,
        role=access.role
    )


# --- Legacy: OAuth2 Token (for backward compatibility) ---
@router.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    기존 OAuth2 호환 (단일 매장 유저용 - 첫 번째 매장으로 자동 선택)
    """
    user = db.query(CommerceUser).filter(CommerceUser.username == form_data.username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    print(f"[AUTH] Legacy login: {user.username}")

    # 첫 번째 접근 가능한 매장 선택
    access = db.query(UserStoreAccess).filter(UserStoreAccess.user_id == user.id).first()

    if not access:
        raise HTTPException(status_code=403, detail="No store access")

    store = db.query(Store).filter(Store.id == access.store_id).first()

    access_token = create_access_token(
        data={
            "sub": user.username,
            "user_id": user.id,
            "store_id": access.store_id,
            "role": access.role,
        },
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "store_id": access.store_id,
        "store_name": store.name if store else None,
        "role": access.role
    }


# --- Register Staff ---
@router.post("/register")
def register_staff(
    username: str,
    password: str,
    store_id: int,
    role: UserRole = UserRole.STAFF,
    db: Session = Depends(get_db)
):
    existing = db.query(CommerceUser).filter(CommerceUser.username == username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already registered")

    # Create user
    new_user = CommerceUser(
        username=username,
        password_hash=get_password_hash(password),
    )
    db.add(new_user)
    db.flush()

    # Create store access
    access = UserStoreAccess(
        user_id=new_user.id,
        store_id=store_id,
        role=role
    )
    db.add(access)
    db.commit()

    return {"status": "created", "user_id": new_user.id, "username": username, "role": role}
