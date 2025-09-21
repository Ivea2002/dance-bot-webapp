"""Application entry point for FastAPI."""

from __future__ import annotations

from fastapi import FastAPI

from app.api.routes import router as api_router

app = FastAPI(title="Dance Bot API")

app.include_router(api_router, prefix="/api")


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Simple health check endpoint."""

    return {"status": "ok"}
