from functools import lru_cache
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


@lru_cache
class Settings(BaseSettings):
    """Application configuration settings."""

    # Application
    app_env: Literal["production", "testing", "development"] = "production"
    app_port: int = 8000
    app_title: str = "Your App Title"
    app_version: str = "1.0.0"
    app_description: str = "Your App Description"

    # Security
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    password_min_length: int = 8
    password_max_length: int = 128

    # Rate Limiting
    rate_limit_requests: int = 100  # Max requests
    rate_limit_time_window: int = 60  # Time window in seconds

    # CORS
    cors_origins: list[str] = ["*"]
    cors_allowed_methods: list[str] = ["*"]
    cors_allowed_headers: list[str] = ["*"]
    cors_allowed_credentials: bool = True

    # Database
    db_host: str = "localhost"
    db_port: int = 5432
    db_user: str
    db_password: str
    db_name: str

    # Cache
    cache_host: str = "localhost"
    cache_port: int = 6379
    cache_db: int = 0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    @property
    def database_url(self) -> str:
        """Constructs the database connection URL."""
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    @property
    def app_debug(self) -> bool:
        """Indicates if the application is running in debug mode."""
        return self.app_env != "production"


settings = Settings()
