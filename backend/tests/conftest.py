"""Shared pytest fixtures."""

import os

# Settings now refuses to start without a database password and a strong JWT
# secret. Supply throwaway values before importing the app so a fresh checkout
# (or CI, which has no .env) can collect tests without real credentials. Any
# value already present in the environment wins.
os.environ.setdefault("APP_ENV", "development")
os.environ.setdefault("POSTGRES_PASSWORD", "test-only-postgres-password")
os.environ.setdefault("JWT_SECRET", "test-only-jwt-secret-value-not-used-in-any-real-deployment")

import pytest  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402

from app.main import app  # noqa: E402


@pytest.fixture
async def client() -> AsyncClient:
    """Async HTTP client bound to the FastAPI application."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
