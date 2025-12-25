from typing import Type
from src.services.base import BaseTGService
from src.services.catalog.sender import TgSenderService
from src.services.catalog.scraper import TgScraperService

class ServiceFactory:
    """
    서비스 코드를 기반으로 적절한 Service Class를 반환합니다.
    """
    _registry = {
        "TG_SENDER_BASIC": TgSenderService,
        "TG_GROUP_SCRAPER": TgScraperService
    }

    @classmethod
    def get_service_class(cls, service_code: str) -> Type[BaseTGService]:
        service_class = cls._registry.get(service_code)
        if not service_class:
            raise ValueError(f"Unknown Service Code: {service_code}")
        return service_class