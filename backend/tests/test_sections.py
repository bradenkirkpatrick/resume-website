"""
Tests for the section ordering API endpoints.
"""

from httpx import AsyncClient

DEFAULT_ORDER = [
    "summary",
    "experience",
    "education",
    "skills",
    "projects",
    "certifications",
]


async def test_get_section_order_default(client: AsyncClient):
    """Test that section order returns the default order initially."""
    response = await client.get("/api/sections/order")
    assert response.status_code == 200
    data = response.json()
    assert data == DEFAULT_ORDER


async def test_update_section_order(client: AsyncClient):
    """Test updating the section order."""
    new_order = ["projects", "skills", "summary", "experience", "education", "certifications"]
    response = await client.put("/api/sections/order", json=new_order)
    assert response.status_code == 200
    data = response.json()
    assert data == new_order

    # Verify persistence
    get_resp = await client.get("/api/sections/order")
    assert get_resp.json() == new_order


async def test_update_section_order_empty_fallback(client: AsyncClient):
    """Test that an empty order falls back to default."""
    response = await client.put("/api/sections/order", json=[])
    assert response.status_code == 200
    assert response.json() == DEFAULT_ORDER


async def test_section_order_persists_across_calls(client: AsyncClient):
    """Test that order persists across multiple requests."""
    await client.put("/api/sections/order", json=[
        "education", "experience", "summary",
    ])
    resp1 = await client.get("/api/sections/order")
    assert resp1.json() == ["education", "experience", "summary"]

    resp2 = await client.get("/api/sections/order")
    assert resp2.json() == ["education", "experience", "summary"]


async def test_section_order_invalid_sections(client: AsyncClient):
    """Test that any string list is accepted (validation happens on frontend)."""
    response = await client.put("/api/sections/order", json=["foo", "bar"])
    assert response.status_code == 200
    assert response.json() == ["foo", "bar"]
