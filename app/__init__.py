"""Core application package."""

from app.api import router as api_router
from app.main import app

__all__ = ["app", "api_router"]
