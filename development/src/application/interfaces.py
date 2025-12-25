from abc import ABC, abstractmethod
from src.domain.schemas import MessageRequest, SendResult

class ISenderService(ABC):
    """
    전송 서비스 인터페이스 (Port)
    모든 구체적인 전송 구현체(Adapter)는 이 클래스를 상속받아야 합니다.
    """
    
    @abstractmethod
    async def send(self, message: MessageRequest) -> SendResult:
        """
        메시지를 전송합니다.
        
        Args:
            message (MessageRequest): 전송할 메시지 객체
            
        Returns:
            SendResult: 전송 성공 여부 및 결과
        """
        pass

    @abstractmethod
    async def validate_connection(self) -> bool:
        """
        전송 서버/API와의 연결 상태를 점검합니다.
        """
        pass