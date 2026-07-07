from pydantic_settings import BaseSettings
from typing import List
import secrets


class Settings(BaseSettings):
    # App
    APP_NAME: str = "NexistPOS"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"

    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 12  # 12 jam (shift kasir)

    # Database
    POSTGRES_USER: str = "pos_user"
    POSTGRES_PASSWORD: str = "pos_password"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "pos_db"

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def DATABASE_URL_SYNC(self) -> str:
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:5173",
        "https://pos.nexisthub.id",
    ]

    TIMEZONE: str = "Asia/Makassar"  # WITA UTC+8

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
