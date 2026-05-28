"""Health-check endpoint."""
from __future__ import annotations

from fastapi import APIRouter

from app.core.config import get_settings

router = APIRouter()


@router.get("/health")
async def health() -> dict[str, str]:
    """Lightweight liveness probe."""
    settings = get_settings()
    return {
        "status": "ok",
        "version": "0.1.0",
        "llm_provider": settings.llm_provider,
    }
