from pydantic_settings import BaseSettings
from pathlib import Path

class SystemSettings(BaseSettings):
    """
    TG-SYSTEM 마스터 설정
    """
    PROJECT_NAME: str = "TG-SYSTEM Enterprise"
    VERSION: str = "3.0.0"
    
    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parents[2]
    LOG_DIR: Path = BASE_DIR / "logs"
    
    # Database
    DB_URL: str = "sqlite:///./tg_master_v3.db"
    
    # Security
    SECRET_KEY: str = "dev_secret"
    
    # Serverless / Docker Config
    DOCKER_SOCKET: str = "unix:///var/run/docker.sock"
    
    class Config:
        env_file = "config/.env"
        env_file_encoding = "utf-8"

settings = SystemSettings()