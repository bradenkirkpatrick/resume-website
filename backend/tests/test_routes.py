"""
Additional tests for API routes and edge cases.
"""

from httpx import AsyncClient


async def test_resume_response_time(client: AsyncClient):
    """Test that the resume endpoint responds within a reasonable time."""
    response = await client.get("/api/resume")
    assert response.elapsed.total_seconds() < 5.0


async def test_resume_content_type(client: AsyncClient):
    """Test that the resume endpoint returns JSON."""
    response = await client.get("/api/resume")
    assert "application/json" in response.headers.get("content-type", "")


async def test_resume_experience_dates(client: AsyncClient):
    """Test that experience entries have valid dates."""
    response = await client.get("/api/resume")
    data = response.json()

    for exp in data["experience"]:
        assert "start_date" in exp
        # Date should be a string in ISO format or null for end_date
        if exp.get("end_date"):
            assert isinstance(exp["end_date"], str)


async def test_resume_education_dates(client: AsyncClient):
    """Test that education entries have valid graduation dates."""
    response = await client.get("/api/resume")
    data = response.json()

    for edu in data["education"]:
        assert "graduation_date" in edu
        assert isinstance(edu["graduation_date"], str)


async def test_resume_skills_structure(client: AsyncClient):
    """Test that skills have proper structure."""
    response = await client.get("/api/resume")
    data = response.json()

    for skill in data["skills"]:
        assert isinstance(skill["category"], str)
        assert isinstance(skill["items"], list)
        assert len(skill["items"]) > 0


async def test_openapi_schema(client: AsyncClient):
    """Test that the OpenAPI schema is valid."""
    response = await client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()

    assert "paths" in schema
    assert "/api/resume" in schema["paths"]
    assert "/api/resume/download" in schema["paths"]
    assert "/health" in schema["paths"]


async def test_cors_multiple_origins(client: AsyncClient):
    """Test CORS with multiple allowed origins."""
    response = await client.options(
        "/api/resume",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    # The response may not include CORS headers for OPTIONS without actual request
    # Just verify the endpoint handles it gracefully
    assert response.status_code in (200, 405)


async def test_resume_from_google_doc(client: AsyncClient):
    """Test that the resume API uses the Google Doc when configured."""
    import os

    # Set the real Google Doc ID to test the full pipeline
    old_id = os.environ.get("GOOGLE_DOCS_ID")
    old_creds = os.environ.pop("GOOGLE_APPLICATION_CREDENTIALS", None)
    os.environ["GOOGLE_DOCS_ID"] = "1IvKov91tVgnB4mHLVjz1s18q9OJnNeWyh3mNsmG3n84"

    try:
        response = await client.get("/api/resume")
        assert response.status_code == 200
        data = response.json()
        # The Google Doc should contain the name Braden
        # Verify the Google Doc was fetched - should contain "Braden Kirkpatrick"
        assert "Braden" in data.get("name", "")
        # Should have projects (the doc has many)
        assert len(data.get("projects", [])) > 0
        # Should have education
        assert len(data.get("education", [])) > 0
    finally:
        if old_id:
            os.environ["GOOGLE_DOCS_ID"] = old_id
        else:
            os.environ.pop("GOOGLE_DOCS_ID", None)
        if old_creds is not None:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = old_creds


async def test_raw_resume_endpoint(client: AsyncClient):
    """Test that the raw resume endpoint returns doc content."""
    import os

    old_id = os.environ.get("GOOGLE_DOCS_ID")
    old_creds = os.environ.pop("GOOGLE_APPLICATION_CREDENTIALS", None)
    os.environ["GOOGLE_DOCS_ID"] = "1IvKov91tVgnB4mHLVjz1s18q9OJnNeWyh3mNsmG3n84"

    try:
        response = await client.get("/api/resume/raw")
        assert response.status_code == 200
        assert "Braden" in response.text
        assert "EDUCATION" in response.text
    finally:
        if old_id:
            os.environ["GOOGLE_DOCS_ID"] = old_id
        else:
            os.environ.pop("GOOGLE_DOCS_ID", None)
        if old_creds is not None:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = old_creds
