"""
Core Configuration Management
Uses pydantic-settings for type-safe, environment-aware config.
"""
from functools import lru_cache
from typing import List, Literal
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ──────────────────────────────────────────────
    app_name: str = "IDEP"
    app_version: str = "1.0.0"
    app_env: Literal["development", "staging", "production"] = "development"
    debug: bool = True
    secret_key: str = "change-me-in-production"

    # ── Server ────────────────────────────────────────────────────
    host: str = "0.0.0.0"
    port: int = 8000

    # ── Database ──────────────────────────────────────────────────
    database_url: str = "postgresql://idep_user:idep_password@localhost:5432/idep_db"
    database_pool_size: int = 10
    database_max_overflow: int = 20

    # ── LLM ───────────────────────────────────────────────────────
    llm_provider: Literal["openai", "anthropic", "azure_openai", "ollama"] = "ollama"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-20250514"
    azure_openai_endpoint: str = ""
    azure_openai_key: str = ""
    azure_openai_deployment: str = ""
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"

    # ── OCR ───────────────────────────────────────────────────────
    ocr_engine: Literal["tesseract", "paddleocr"] = "tesseract"
    tesseract_cmd: str = "/usr/bin/tesseract"
    ocr_language: str = "eng"

    # ── File Upload ───────────────────────────────────────────────
    upload_dir: str = "./uploads"
    max_file_size_mb: int = 10
    allowed_extensions: str = "pdf,png,jpg,jpeg,tiff"

    # ── Logging ───────────────────────────────────────────────────
    log_level: str = "INFO"
    log_file: str = "./logs/idep.log"
    log_rotation: str = "10 MB"
    log_retention: str = "30 days"

    # ── Streamlit ─────────────────────────────────────────────────
    streamlit_port: int = 8501
    api_base_url: str = "http://localhost:8000"

    @property
    def allowed_extensions_list(self) -> List[str]:
        return [ext.strip().lower() for ext in self.allowed_extensions.split(",")]

    @property
    def max_file_size_bytes(self) -> int:
        return self.max_file_size_mb * 1024 * 1024

    @field_validator("database_url")
    @classmethod
    def validate_db_url(cls, v: str) -> str:
        if not v.startswith(("postgresql://", "postgresql+asyncpg://", "sqlite:///")):
            raise ValueError("Only PostgreSQL and SQLite are supported")
        return v


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance — call this everywhere."""
    return Settings()
