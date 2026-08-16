"""
Centralized application configuration.

All secrets and environment-specific values are read from environment
variables (via a `.env` file locally, or real environment variables in
production). Nothing here is ever hardcoded to a real credential.
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # CognoDB / Neo4j driver connection
    cognodb_uri: str = "bolt+s://localhost:7687"
    cognodb_username: str = "cognodb"
    cognodb_password: str = ""
    cognodb_database: str = "neo4j"

    # API
    cors_origins: str = "http://localhost:5173"
    log_level: str = "INFO"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Settings are read once and cached for the lifetime of the process."""
    return Settings()
