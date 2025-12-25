from abc import ABC, abstractmethod
from typing import Dict, Any
from src.core.database.v3_schema import AuditLog

class ServerlessContext:
    """
    서버리스 실행 환경 컨텍스트
    (Request ID, User Info, Remaining Time 등)
    """
    def __init__(self, req_id: str, user_id: str):
        self.req_id = req_id
        self.user_id = user_id

class BaseFunction(ABC):
    """
    모든 TG 서비스 함수가 상속받아야 할 기본 클래스.
    설계의 'TG_Serverless_Architecture'를 준수합니다.
    """
    
    def __init__(self, context: ServerlessContext):
        self.context = context
    
    @abstractmethod
    def handle(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        메인 로직. 
        :param event: 입력 페이로드 (JSON)
        :return: 실행 결과 (JSON)
        """
        pass

    def audit(self, action: str, details: str):
        """법적 증빙 로그 기록 (DB 직렬화는 별도 처리)"""
        print(f"[AUDIT] Req: {self.context.req_id} | User: {self.context.user_id} | Action: {action} | {details}")