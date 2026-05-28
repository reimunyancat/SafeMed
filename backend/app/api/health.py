from __future__ import annotations

from fastapi import APIRouter, Request

from app.core.config import get_settings

router = APIRouter()


@router.get("/health")
async def health(request: Request) -> dict[str, str]:
    """Lightweight liveness probe."""
    settings = get_settings()
    return {
        "status": "ok",
        "version": request.app.version,
        "llm_provider": settings.llm_provider,
    }