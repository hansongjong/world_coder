import uuid
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Any

from src.database.engine import get_db
from src.core.database.v3_schema import ExecutionRequest, FunctionCatalog, MasterUser, AuditLog
from src.core.kernel import SystemKernel
from src.api.deps import get_current_user # 보안 의존성

router = APIRouter(prefix="/v3", tags=["V3 Serverless API"])

# DTO
class RunFunctionRequest(BaseModel):
    function_code: str
    payload: Dict[str, Any]

class ExecutionResponse(BaseModel):
    req_id: str
    status: str
    message: str

def run_kernel_background(req_id: str, db: Session):
    kernel = SystemKernel(db)
    try:
        kernel.invoke_function(req_id)
    except Exception as e:
        print(f"Background Task Error: {e}")

@router.post("/run", response_model=ExecutionResponse)
def execute_function(
    req: RunFunctionRequest, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: MasterUser = Depends(get_current_user) # <--- 보안 적용 완료
):
    """
    [Secured] 서버리스 함수 실행 요청
    Requires: Bearer Token
    """
    # 1. 함수 존재 확인
    fn = db.query(FunctionCatalog).filter_by(function_code=req.function_code).first()
    if not fn:
        raise HTTPException(status_code=404, detail="Function Code not found")

    # 2. 요청 기록 (Pending) - 호출한 사용자 ID(current_user.user_id) 자동 주입
    req_id = f"req-{uuid.uuid4()}"
    new_request = ExecutionRequest(
        req_id=req_id,
        function_code=req.function_code,
        user_id=current_user.user_id, # 토큰에서 추출한 안전한 ID
        input_payload=req.payload,
        status="QUEUED"
    )
    db.add(new_request)
    db.commit()

    # 3. 비동기 실행 트리거
    background_tasks.add_task(run_kernel_background, req_id, db)

    return ExecutionResponse(
        req_id=req_id,
        status="QUEUED",
        message="Function execution queued successfully."
    )

@router.get("/audit/me")
def get_my_audit_logs(
    db: Session = Depends(get_db),
    current_user: MasterUser = Depends(get_current_user)
):
    """
    [Secured] 내 감사 로그 조회
    """
    logs = db.query(AuditLog).filter_by(actor_id=current_user.user_id).order_by(AuditLog.created_at.desc()).limit(50).all()
    return logs