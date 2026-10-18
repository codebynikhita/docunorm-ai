from functools import lru_cache

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application Settings loaded from environment variables or .env file.
    Follows Twelve-Factor App methodology for enterprise configuration.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application Environment
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "docunorm_insecure_development_secret_key_change_in_production"

    # PostgreSQL Database Credentials
    POSTGRES_USER: str = "docunorm_admin"
    POSTGRES_PASSWORD: str = "docunorm_dev_password_change_me"
    POSTGRES_HOST: str = (
        "localhost"  # 'localhost' for local development; 'postgres' inside docker
    )
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "docunorm"

    # Redis Cache & Task Broker
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    # Backend API Networking
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    # AI & Retrieval Models
    EMBEDDING_MODEL_NAME: str = "BAAI/bge-m3"
    RERANKER_MODEL_NAME: str = "BAAI/bge-reranker-large"
    STORAGE_DIR: str = "./storage"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def async_database_url(self) -> str:
        """
        Asynchronous PostgreSQL connection URI using the asyncpg driver.
        Format: postgresql+asyncpg://user:password@host:port/database
        """
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def sync_database_url(self) -> str:
        """
        Synchronous PostgreSQL connection URI using psycopg driver.
        Used for migrations, schema creation, and admin scripts.
        """
        return (
            f"postgresql+psycopg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


@lru_cache
def get_settings() -> Settings:
    """
    Returns cached instance of Settings to avoid re-reading .env on every request.
    """
    return Settings()
