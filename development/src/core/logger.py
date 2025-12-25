import sys
from pathlib import Path
from loguru import logger
from src.core.config import settings

# 로그 저장 경로 설정
LOG_DIR = Path(__file__).resolve().parents[2] / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

class LoggerSetup:
    """
    전역 로깅 설정 클래스.
    Console 출력 및 일별 로그 파일 저장을 처리합니다.
    """
    
    @classmethod
    def setup_logging(cls):
        # 기존 로거 핸들러 제거 (중복 방지)
        logger.remove()

        # 1. 콘솔 출력 (개발용)
        logger.add(
            sys.stderr,
            level="DEBUG" if settings.DEBUG else "INFO",
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
        )

        # 2. 파일 출력 (운영용 - JSON 형식 권장, 여기선 가독성 위주 텍스트)
        logger.add(
            str(LOG_DIR / "system.log"),
            rotation="10 MB",  # 10MB 마다 파일 분할
            retention="10 days", # 10일 보관
            compression="zip", # 압축 저장
            level="INFO",
            encoding="utf-8"
        )
        
        # 3. 에러 전용 로그
        logger.add(
            str(LOG_DIR / "error.log"),
            rotation="5 MB",
            retention="30 days",
            level="ERROR",
            encoding="utf-8",
            backtrace=True,
            diagnose=True
        )

        logger.info(f"Logger initialized. Mode: {'DEBUG' if settings.DEBUG else 'RELEASE'}")

# 초기화 함수 노출
setup_logging = LoggerSetup.setup_logging