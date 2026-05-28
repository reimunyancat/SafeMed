"""FastAPI routers."""
from app.api import analyze, health, medicines

__all__ = ["analyze", "health", "medicines"]
