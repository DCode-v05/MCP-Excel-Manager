# backend/config.py
from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Central configuration for the Salesforce MCP project.

    Values are loaded from environment variables and optionally a .env file.
    """

    # ---- General ----
    ENV: str = Field(default="dev", description="Environment name: dev/stage/prod")
    DEBUG: bool = Field(default=True, description="Enable debug mode")
    API_PREFIX: str = "/api"

    # ---- Logging ----
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_DIR: Path = Field(default=Path("logs"), description="Directory for log files")

    # ---- Gemini API ----
    GEMINI_API_KEY: str = Field(..., description="API key for Google Gemini")

    # ---- Excel / MCP ----
    EXCEL_DATA_DIR: Path = Field(
        default=Path("excel_data"),
        description="Directory where Excel files are stored",
    )

    # ---- CORS / Frontend ----
    FRONTEND_ORIGIN: AnyHttpUrl = Field(
        default="http://localhost:5173",
        description="Frontend origin for CORS",
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Cached settings object so we don't re-parse env on every import.
    """
    settings = Settings()
    # Ensure log directory exists
    settings.LOG_DIR.mkdir(parents=True, exist_ok=True)
    settings.EXCEL_DATA_DIR.mkdir(parents=True, exist_ok=True)
    return settings