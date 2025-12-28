from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import json

from src.database.engine import get_db
from src.commerce.domain.models import Store, StoreConfig, BizType
from src.commerce.auth.security import get_current_user

router = APIRouter(prefix="/store", tags=["Commerce: Store Config"])

# =====================================================
# DTOs
# =====================================================

class StoreConfigResponse(BaseModel):
    store_id: int
    store_name: str
    biz_type: str

    # Modules
    mod_payment: bool
    mod_queue: bool
    mod_reservation: bool
    mod_inventory: bool
    mod_crm: bool
    mod_delivery: bool
    mod_iot: bool
    mod_subscription: bool
    mod_invoice: bool

    # UI Settings
    ui_mode: str
    table_count: int
    deposit_amount: int
    extra_settings: Optional[dict] = None


class StoreConfigUpdate(BaseModel):
    biz_type: Optional[str] = None

    mod_payment: Optional[bool] = None
    mod_queue: Optional[bool] = None
    mod_reservation: Optional[bool] = None
    mod_inventory: Optional[bool] = None
    mod_crm: Optional[bool] = None
    mod_delivery: Optional[bool] = None
    mod_iot: Optional[bool] = None
    mod_subscription: Optional[bool] = None
    mod_invoice: Optional[bool] = None

    ui_mode: Optional[str] = None
    table_count: Optional[int] = None
    deposit_amount: Optional[int] = None
    extra_settings: Optional[dict] = None


class StoreTemplateApply(BaseModel):
    template: str  # CAFE_BASIC, RESTAURANT_PREMIUM, GYM_UNMANNED, RETAIL_WHOLESALE


# =====================================================
# Template Definitions
# =====================================================

STORE_TEMPLATES = {
    "CAFE_BASIC": {
        "biz_type": "cafe",
        "mod_payment": True,
        "mod_queue": True,
        "mod_reservation": False,
        "mod_inventory": False,
        "mod_crm": False,
        "mod_delivery": False,
        "mod_iot": False,
        "mod_subscription": False,
        "mod_invoice": False,
        "ui_mode": "KIOSK_LITE",
        "table_count": 0,
        "deposit_amount": 0,
    },
    "RESTAURANT_PREMIUM": {
        "biz_type": "restaurant",
        "mod_payment": True,
        "mod_queue": False,
        "mod_reservation": True,
        "mod_inventory": True,
        "mod_crm": True,
        "mod_delivery": False,
        "mod_iot": False,
        "mod_subscription": False,
        "mod_invoice": False,
        "ui_mode": "TABLE_MANAGER",
        "table_count": 20,
        "deposit_amount": 10000,
    },
    "GYM_UNMANNED": {
        "biz_type": "gym",
        "mod_payment": False,
        "mod_queue": False,
        "mod_reservation": False,
        "mod_inventory": False,
        "mod_crm": True,
        "mod_delivery": False,
        "mod_iot": True,
        "mod_subscription": True,
        "mod_invoice": False,
        "ui_mode": "ADMIN_DASHBOARD",
        "table_count": 0,
        "deposit_amount": 0,
    },
    "RETAIL_WHOLESALE": {
        "biz_type": "retail",
        "mod_payment": False,
        "mod_queue": False,
        "mod_reservation": False,
        "mod_inventory": True,
        "mod_crm": False,
        "mod_delivery": True,
        "mod_iot": False,
        "mod_subscription": False,
        "mod_invoice": True,
        "ui_mode": "ERP_LITE",
        "table_count": 0,
        "deposit_amount": 0,
    },
    "BEAUTY_SALON": {
        "biz_type": "beauty",
        "mod_payment": True,
        "mod_queue": True,
        "mod_reservation": True,
        "mod_inventory": False,
        "mod_crm": True,
        "mod_delivery": False,
        "mod_iot": False,
        "mod_subscription": False,
        "mod_invoice": False,
        "ui_mode": "TABLE_MANAGER",
        "table_count": 0,
        "deposit_amount": 10000,
    },
}


# =====================================================
# Endpoints
# =====================================================

@router.get("/config/{store_id}", response_model=StoreConfigResponse)
def get_store_config(store_id: int, db: Session = Depends(get_db)):
    """[설정 조회] 매장 설정 및 활성화된 모듈 조회"""
    store = db.get(Store, store_id)
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")

    config = db.query(StoreConfig).filter_by(store_id=store_id).first()

    # Create default config if not exists
    if not config:
        config = StoreConfig(store_id=store_id)
        db.add(config)
        db.commit()
        db.refresh(config)

    extra = None
    if config.extra_settings:
        try:
            extra = json.loads(config.extra_settings)
        except json.JSONDecodeError:
            extra = None

    return StoreConfigResponse(
        store_id=store.id,
        store_name=store.name,
        biz_type=store.biz_type or "cafe",
        mod_payment=config.mod_payment,
        mod_queue=config.mod_queue,
        mod_reservation=config.mod_reservation,
        mod_inventory=config.mod_inventory,
        mod_crm=config.mod_crm,
        mod_delivery=config.mod_delivery,
        mod_iot=config.mod_iot,
        mod_subscription=config.mod_subscription,
        mod_invoice=config.mod_invoice,
        ui_mode=config.ui_mode,
        table_count=config.table_count,
        deposit_amount=config.deposit_amount,
        extra_settings=extra,
    )


@router.put("/config/{store_id}", response_model=StoreConfigResponse)
def update_store_config(
    store_id: int,
    req: StoreConfigUpdate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """[설정 수정] 매장 설정 업데이트"""
    if user["role"] not in ["owner", "admin"]:
        raise HTTPException(status_code=403, detail="Only owners can update config")

    if user["store_id"] != store_id and user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not your store")

    store = db.get(Store, store_id)
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")

    config = db.query(StoreConfig).filter_by(store_id=store_id).first()
    if not config:
        config = StoreConfig(store_id=store_id)
        db.add(config)

    # Update store biz_type if provided
    if req.biz_type:
        store.biz_type = req.biz_type

    # Update config fields
    update_data = req.dict(exclude_unset=True, exclude={"biz_type", "extra_settings"})
    for key, value in update_data.items():
        setattr(config, key, value)

    # Handle extra_settings as JSON
    if req.extra_settings is not None:
        config.extra_settings = json.dumps(req.extra_settings)

    db.commit()
    db.refresh(config)

    return get_store_config(store_id, db)


@router.post("/config/{store_id}/template")
def apply_template(
    store_id: int,
    req: StoreTemplateApply,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """[템플릿 적용] 사전 정의된 업종별 설정 템플릿 적용"""
    if user["role"] not in ["owner", "admin"]:
        raise HTTPException(status_code=403, detail="Only owners can apply templates")

    if req.template not in STORE_TEMPLATES:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown template. Available: {list(STORE_TEMPLATES.keys())}"
        )

    template = STORE_TEMPLATES[req.template]

    store = db.get(Store, store_id)
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")

    config = db.query(StoreConfig).filter_by(store_id=store_id).first()
    if not config:
        config = StoreConfig(store_id=store_id)
        db.add(config)

    # Apply template values
    store.biz_type = template.get("biz_type", "cafe")

    for key, value in template.items():
        if key != "biz_type" and hasattr(config, key):
            setattr(config, key, value)

    db.commit()

    return {
        "status": "applied",
        "template": req.template,
        "store_id": store_id
    }


@router.get("/templates")
def list_templates():
    """[템플릿 목록] 사용 가능한 업종별 템플릿 목록"""
    result = []
    for name, config in STORE_TEMPLATES.items():
        enabled_modules = [
            k.replace("mod_", "") for k, v in config.items()
            if k.startswith("mod_") and v is True
        ]
        result.append({
            "name": name,
            "biz_type": config.get("biz_type"),
            "ui_mode": config.get("ui_mode"),
            "enabled_modules": enabled_modules
        })
    return result


@router.get("/{store_id}")
def get_store_info(store_id: int, db: Session = Depends(get_db)):
    """[매장 정보] 기본 매장 정보 조회"""
    store = db.get(Store, store_id)
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")

    return {
        "id": store.id,
        "name": store.name,
        "address": store.address,
        "biz_number": store.biz_number,
        "biz_type": store.biz_type,
        "is_active": store.is_active
    }
