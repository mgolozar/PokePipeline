"""Configuration management using pydantic-settings."""

from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with validation."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Database settings
    DATABASE_URL: str = Field(
        default="postgresql+psycopg://postgres:postgres@db:5432/poke",
        description="Database connection string",
    )

    # HTTP settings
    HTTP_CONCURRENCY: int = Field(
        default=5,
        description="Number of concurrent HTTP requests",
        ge=1,
        le=100,
    )
    RATE_LIMIT_PER_SEC: int = Field(
        default=4,
        description="Rate limit (requests per second)",
        ge=1,
    )
    REQUEST_TIMEOUT_SEC: int = Field(
        default=10,
        description="HTTP request timeout in seconds",
        ge=1,
        le=300,
    )

    # Target settings
    TARGET_LIMIT: int = Field(
        default=20,
        description="Number of Pokémon to fetch",
        ge=1,
    )
    TARGET_OFFSET: int = Field(
        default=0,
        description="Offset for Pokémon fetching",
        ge=0,
    )
    ENABLE_EVOLUTION: bool = Field(
        default=False,
        description="Enable fetching evolution chain data",
    )

    # Optional settings
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Logging level",
    )
    API_BASE_URL: str = Field(
        default="https://pokeapi.co/api/v2",
        description="Base URL for PokeAPI",
    )


# Global settings instance
settings = Settings()

