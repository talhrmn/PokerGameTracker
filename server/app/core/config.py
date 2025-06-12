from typing import List, Optional
from pydantic import AnyHttpUrl, validator
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
import secrets

load_dotenv()


class Settings(BaseSettings):
    # API Settings
    APP_NAME: str = "PokerTracker API"
    API_PREFIX: str = "/api"
    API_V1_STR: str = "/v1"
    DEBUG: bool = False
    
    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 1
    
    # MongoDB Settings
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "poker_game_tracker"
    MONGODB_MAX_CONNECTIONS: int = 100
    MONGODB_MIN_CONNECTIONS: int = 1
    MONGODB_MAX_IDLE_TIME_MS: int = 30000
    
    # Security Settings
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS Settings
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Logging Settings
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
