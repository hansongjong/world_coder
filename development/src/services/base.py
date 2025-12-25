from abc import ABC, abstractmethod
from typing import Dict, Any
from sqlalchemy.orm import Session
from src.core.logger import logger
from src.database.models import Deployment, SystemLog

class BaseTGService(ABC):
    """
    모든 TG 서비스(Bot, Crawler)의 기본 클래스
    """
    def __init__(self, deployment_id: str, config: Dict[str, Any], db: Session):
        self.deployment_id = deployment_id
        self.config = config
        self.db = db
        self.logger = logger.bind(deployment_id=deployment_id)

    def log(self, message: str, level: str = "INFO"):
        """DB에 로그를 남깁니다."""
        new_log = SystemLog(
            deployment_id=self.deployment_id,
            level=level,
            action_type=self.__class__.__name__,
            message=message
        )
        self.db.add(new_log)
        self.db.commit()
        # 콘솔에도 출력
        if level == "ERROR":
            self.logger.error(message)
        else:
            self.logger.info(message)

    @abstractmethod
    async def setup(self):
        """리소스 초기화, 세션 연결 등"""
        pass

    @abstractmethod
    async def run(self):
        """실제 비즈니스 로직 실행"""
        pass

    @abstractmethod
    async def cleanup(self):
        """리소스 정리"""
        pass

    async def execute(self):
        """템플릿 메소드 패턴: 실행 흐름 제어"""
        try:
            self.log("Starting service initialization...")
            await self.setup()
            
            self.log("Executing main logic...")
            await self.run()
            
            self.log("Service completed successfully.")
        except Exception as e:
            self.log(f"Service Execution Failed: {str(e)}", level="ERROR")
            raise e
        finally:
            await self.cleanup()