"""
Pytest configuration and shared fixtures for the Resume Website tests.
"""

import os
from typing import AsyncIterator

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

# Set database to in-memory SQLite for tests BEFORE importing app modules
os.environ["DATABASE_URL"] = "sqlite:///./test_resume.db"

from app.database import Base, SessionLocal, init_db  # noqa: E402
from app.main import app as _app  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Create all tables once per test session."""
    init_db()
    yield
    # Clean up test database
    import gc
    gc.collect()
    if os.path.exists("test_resume.db"):
        os.remove("test_resume.db")


@pytest.fixture(autouse=True)
def clear_db():
    """Clear all data between tests using SQLAlchemy 2.0 style."""
    from app.database import engine as db_engine

    with db_engine.connect() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())
        conn.commit()


@pytest.fixture
def app() -> FastAPI:
    """Return the FastAPI application instance."""
    return _app


@pytest.fixture
async def client(app: FastAPI) -> AsyncIterator[AsyncClient]:
    """Return an async test client for the FastAPI app."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as async_client:
        yield async_client


@pytest.fixture(autouse=True)
def reset_env():
    """Reset environment variables before each test."""
    original_env = os.environ.copy()
    os.environ["CORS_ORIGINS"] = "http://localhost:5173"
    os.environ["ENVIRONMENT"] = "test"
    os.environ["SECRET_KEY"] = "test-secret-key"
    os.environ["DATABASE_URL"] = "sqlite:///./test_resume.db"

    # Clear Google Docs env vars so tests use fallback data
    if "GOOGLE_DOCS_ID" in os.environ:
        del os.environ["GOOGLE_DOCS_ID"]
    if "GOOGLE_APPLICATION_CREDENTIALS" in os.environ:
        del os.environ["GOOGLE_APPLICATION_CREDENTIALS"]

    yield

    os.environ.clear()
    os.environ.update(original_env)
