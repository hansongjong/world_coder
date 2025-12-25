import importlib
import traceback
from datetime import datetime
from sqlalchemy.orm import Session
from src.core.database.v3_schema import ExecutionRequest, FunctionCatalog
from src.core.serverless.handler import ServerlessContext
from src.core.erp_service import ERPService, LegalAuditService

class SystemKernel:
    """
    TG-SYSTEM Enterprise Kernel V2
    Integrated with ERP & Legal Compliance
    """
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.erp = ERPService(db_session)
        self.legal = LegalAuditService(db_session)

    def invoke_function(self, req_id: str):
        # 1. 요청 로드
        request = self.db.query(ExecutionRequest).filter_by(req_id=req_id).first()
        if not request:
            return

        user_id = request.user_id
        fn_code = request.function_code

        # 2. [ERP] 사전 검증 (Billing Check)
        if not self.erp.check_billing_eligibility(user_id, service_cost=100):
            request.status = "DENIED_BILLING"
            request.result_output = {"error": "Insufficient balance or invalid subscription"}
            self.legal.log_action(req_id, user_id, "EXECUTION_DENIED", "Billing check failed")
            self.db.commit()
            return

        # 3. 메타데이터 로드
        function_meta = self.db.query(FunctionCatalog).filter_by(function_code=fn_code).first()
        if not function_meta:
            request.status = "FAILED"
            self.db.commit()
            return

        # 4. 상태 업데이트 및 감사 로그 시작
        request.status = "PROCESSING"
        self.db.commit()
        self.legal.log_action(req_id, user_id, "EXECUTION_START", f"Function: {fn_code}")

        start_time = datetime.now()
        
        try:
            # 5. 동적 모듈 실행
            module_name, class_name = function_meta.handler_path.rsplit(".", 1)
            module = importlib.import_module(module_name)
            HandlerClass = getattr(module, class_name)
            
            context = ServerlessContext(req_id=req_id, user_id=user_id)
            handler = HandlerClass(context)
            
            # 실행
            result = handler.handle(request.input_payload)
            
            # 6. 성공 처리
            request.status = "COMPLETED"
            request.result_output = result
            
            # [ERP] 과금 확정
            self.erp.process_billing(user_id, fn_code, 100)
            
        except Exception as e:
            # 7. 실패 처리
            traceback.print_exc()
            request.status = "FAILED"
            request.result_output = {"error": str(e)}
            self.legal.log_action(req_id, user_id, "EXECUTION_ERROR", str(e))
        
        finally:
            end_time = datetime.now()
            request.execution_time_ms = int((end_time - start_time).total_seconds() * 1000)
            self.legal.log_action(req_id, user_id, "EXECUTION_END", f"Status: {request.status}")
            self.db.commit()