from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

LLMProvider = Literal["nim", "upstage", "ollama", "none"]

_BACKEND_DIR = Path(__file__).resolve().parents[2]
_ENV_PATH = _BACKEND_DIR / ".env"


class Settings(BaseSettings):
    """Loaded from `backend/.env` plus process environment."""

    model_config = SettingsConfigDict(
        env_file=str(_ENV_PATH),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    mfds_service_key: str = Field(
        "",
        description=(
            "data.go.kr service key. Pass through as-is when "
            "MFDS_KEY_IS_URL_ENCODED=true (no httpx params=)."
        ),
    )
    mfds_key_is_url_encoded: bool = True
    mfds_base_url: str = "https://apis.data.go.kr/1471000"

    llm_provider: LLMProvider = "nim"
    nim_api_key: str = ""
    nim_base_url: str = "https://integrate.api.nvidia.com/v1"
    nim_model: str = "meta/llama-3.1-70b-instruct"
    upstage_api_key: str = ""
    upstage_model: str = "solar-pro"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "exaone3.5:7.8b"

    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://localhost:4173",
    ]
    log_level: str = "INFO"
    cache_db_path: str = "../data/cache/safemed_cache.sqlite"
    cache_ttl_hours: int = 24


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Cached settings accessor."""
    return Settings()