"""
Tests for the main FastAPI application module.
"""

from httpx import AsyncClient


async def test_health_endpoint(client: AsyncClient):
    """Test that the health check endpoint returns healthy status."""
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


async def test_app_title(client: AsyncClient):
    """Test that the API docs title is correct."""
    response = await client.get("/openapi.json")
    assert response.status_code == 200
    assert response.json()["info"]["title"] == "Resume Website API"


async def test_app_version(client: AsyncClient):
    """Test that the API version is correct."""
    response = await client.get("/openapi.json")
    assert response.status_code == 200
    assert response.json()["info"]["version"] == "1.0.0"


async def test_cors_headers(client: AsyncClient):
    """Test that CORS headers are present in responses."""
    response = await client.options(
        "/health",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers


async def test_not_found(client: AsyncClient):
    """Test that unknown routes return 404."""
    response = await client.get("/nonexistent")
    assert response.status_code == 404


async def test_resume_endpoint_exists(client: AsyncClient):
    """Test that the resume API endpoint is accessible."""
    response = await client.get("/api/resume")
    assert response.status_code == 200


async def test_download_endpoint_exists(client: AsyncClient):
    """Test that the download endpoint is accessible."""
    response = await client.get("/api/resume/download")
    assert response.status_code == 200
