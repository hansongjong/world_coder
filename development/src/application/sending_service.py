from typing import Dict
from src.application.interfaces import ISenderService
from src.domain.schemas import MessageRequest, SendResult, ChannelType
from src.core.logger import logger

class SendingService:
    """
    메시지 전송을 조율하는 서비스 클래스.
    적절한 어댑터를 선택하여 전송을 위임합니다.
    """
    
    def __init__(self, strategies: Dict[ChannelType, ISenderService]):
        self.strategies = strategies

    async def dispatch(self, request: MessageRequest) -> SendResult:
        """
        요청된 채널에 맞는 어댑터를 찾아 전송을 실행합니다.
        """
        adapter = self.strategies.get(request.channel)
        
        if not adapter:
            msg = f"No adapter configured for channel: {request.channel}"
            logger.error(msg)
            return SendResult(
                success=False, 
                request_id=request.request_id, 
                error_code="UNSUPPORTED_CHANNEL", 
                message=msg
            )
            
        # 전송 실행
        logger.info(f"Dispatching message via {request.channel.value.upper()}...")
        result = await adapter.send(request)
        return result