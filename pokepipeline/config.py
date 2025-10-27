"""Configuration management."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    DATABASE_URL: str = "postgresql+psycopg://postgres:postgres@localhost:5432/poke"
    HTTP_CONCURRENCY: int = Field(default=5, ge=1, le=100)
    RATE_LIMIT_PER_SEC: int = Field(default=4, ge=1)
    REQUEST_TIMEOUT_SEC: int = Field(default=10, ge=1, le=300)
    TARGET_LIMIT: int = Field(default=20, ge=1)
    TARGET_OFFSET: int = Field(default=0, ge=0)
    ENABLE_EVOLUTION: bool = False
    LOG_LEVEL: str = "INFO"
    API_BASE_URL: str = "https://pokeapi.co/api/v2"
    TRANSFORM_ENABLE_ENRICH: bool = Field(default=True)


settings = Settings()

