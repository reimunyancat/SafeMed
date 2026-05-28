"""SafeMed FastAPI entry point."""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import analyze, health, medicines
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title="SafeMed API",
    version="0.2.0",
    description=(
        "Multi-drug interaction risk assessment for elderly and polypharmacy "
        "patients (KR market)."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(medicines.router, prefix="/api", tags=["medicines"])
app.include_router(analyze.router, prefix="/api", tags=["analyze"])
