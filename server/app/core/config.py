from typing import List

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    APP_NAME: str = "PokerTracker API"
    API_PREFIX: str = "/api"
    DEBUG: bool = False

    MONGODB_URL: str
    MONGODB_DB_NAME: str

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    CORS_ORIGINS: List[str]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
