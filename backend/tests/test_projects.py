"""
Tests for the project management API endpoints.
"""

from httpx import AsyncClient


async def test_list_projects_empty(client: AsyncClient):
    """Test that listing projects returns an empty list initially."""
    response = await client.get("/api/projects")
    assert response.status_code == 200
    assert response.json() == []


async def test_create_project_minimal(client: AsyncClient):
    """Test creating a project with minimal required fields."""
    response = await client.post("/api/projects", json={
        "title": "Test Project",
        "start_month": 1,
        "start_year": 2024,
    })
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Project"
    assert data["start_month"] == 1
    assert data["start_year"] == 2024
    assert data["end_month"] is None
    assert data["end_year"] is None
    assert data["technologies"] == []
    assert data["frameworks"] == []
    assert data["languages"] == []
    assert data["bullet_points"] == []
    assert data["tags"] == []
    assert "id" in data

    # Cleanup
    await client.delete(f"/api/projects/{data['id']}")


async def test_create_project_full(client: AsyncClient):
    """Test creating a project with all fields."""
    response = await client.post("/api/projects", json={
        "title": "Full Stack App",
        "start_month": 3,
        "start_year": 2023,
        "end_month": 6,
        "end_year": 2024,
        "languages": ["Python", "TypeScript"],
        "frameworks": ["React", "FastAPI"],
        "technologies": ["PostgreSQL", "Docker"],
        "bullet_points": ["Built the frontend", "Designed the API", "Deployed to AWS"],
        "tags": ["web", "full-stack", "production"],
    })
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Full Stack App"
    assert len(data["languages"]) == 2
    assert "Python" in data["languages"]
    assert len(data["frameworks"]) == 2
    assert "React" in data["frameworks"]
    assert len(data["technologies"]) == 2
    assert "Docker" in data["technologies"]
    assert len(data["bullet_points"]) == 3
    assert data["bullet_points"][0] == "Built the frontend"
    assert len(data["tags"]) == 3
    assert "web" in data["tags"]
    assert data["end_month"] == 6
    assert data["end_year"] == 2024

    # Cleanup
    await client.delete(f"/api/projects/{data['id']}")


async def test_create_project_invalid(client: AsyncClient):
    """Test that creating a project with invalid data returns 422."""
    response = await client.post("/api/projects", json={
        "title": "",
        "start_month": 13,
        "start_year": 2024,
    })
    assert response.status_code == 422


async def test_get_project(client: AsyncClient):
    """Test getting a single project by ID."""
    # Create first
    create_resp = await client.post("/api/projects", json={
        "title": "Get Test",
        "start_month": 6,
        "start_year": 2024,
    })
    project_id = create_resp.json()["id"]

    # Get by ID
    response = await client.get(f"/api/projects/{project_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Get Test"

    # Cleanup
    await client.delete(f"/api/projects/{project_id}")


async def test_get_project_not_found(client: AsyncClient):
    """Test getting a nonexistent project returns 404."""
    response = await client.get("/api/projects/99999")
    assert response.status_code == 404


async def test_list_projects_after_create(client: AsyncClient):
    """Test that listing projects returns created projects."""
    await client.post("/api/projects", json={
        "title": "Project A",
        "start_month": 1,
        "start_year": 2024,
    })
    await client.post("/api/projects", json={
        "title": "Project B",
        "start_month": 3,
        "start_year": 2023,
    })

    response = await client.get("/api/projects")
    assert response.status_code == 200
    data = response.json()
    # Should be ordered newest first
    assert len(data) >= 2

    # Cleanup all
    for proj in data:
        await client.delete(f"/api/projects/{proj['id']}")


async def test_update_project(client: AsyncClient):
    """Test updating a project."""
    create_resp = await client.post("/api/projects", json={
        "title": "Original Title",
        "start_month": 1,
        "start_year": 2024,
    })
    project_id = create_resp.json()["id"]

    # Update
    response = await client.put(f"/api/projects/{project_id}", json={
        "title": "Updated Title",
        "languages": ["Go", "Rust"],
        "frameworks": ["Next.js"],
        "technologies": ["Docker", "Kubernetes"],
        "tags": ["devops"],
    })
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert "Go" in data["languages"]
    assert "Next.js" in data["frameworks"]
    assert "Docker" in data["technologies"]
    assert "devops" in data["tags"]

    # Cleanup
    await client.delete(f"/api/projects/{project_id}")


async def test_update_project_not_found(client: AsyncClient):
    """Test updating a nonexistent project returns 404."""
    response = await client.put("/api/projects/99999", json={"title": "Nope"})
    assert response.status_code == 404


async def test_delete_project(client: AsyncClient):
    """Test deleting a project."""
    create_resp = await client.post("/api/projects", json={
        "title": "Delete Me",
        "start_month": 12,
        "start_year": 2024,
    })
    project_id = create_resp.json()["id"]

    response = await client.delete(f"/api/projects/{project_id}")
    assert response.status_code == 204

    # Verify gone
    get_resp = await client.get(f"/api/projects/{project_id}")
    assert get_resp.status_code == 404


async def test_delete_project_not_found(client: AsyncClient):
    """Test deleting a nonexistent project returns 404."""
    response = await client.delete("/api/projects/99999")
    assert response.status_code == 404


async def test_tags_auto_created(client: AsyncClient):
    """Test that tags are automatically created and reused."""
    resp1 = await client.post("/api/projects", json={
        "title": "Tag Test 1",
        "start_month": 1,
        "start_year": 2024,
        "tags": ["python", "web"],
    })
    id1 = resp1.json()["id"]

    resp2 = await client.post("/api/projects", json={
        "title": "Tag Test 2",
        "start_month": 2,
        "start_year": 2024,
        "tags": ["python", "data-science"],
    })
    id2 = resp2.json()["id"]

    # Check tags endpoint
    tags_resp = await client.get("/api/projects/tags/all")
    assert tags_resp.status_code == 200
    tags = tags_resp.json()
    assert "python" in tags
    assert "web" in tags
    assert "data-science" in tags

    # Cleanup
    await client.delete(f"/api/projects/{id1}")
    await client.delete(f"/api/projects/{id2}")


async def test_project_with_tech_categories(client: AsyncClient):
    """Test creating a project with all three tech categories."""
    response = await client.post("/api/projects", json={
        "title": "Tech Demo",
        "start_month": 5,
        "start_year": 2024,
        "languages": ["Python", "JavaScript"],
        "frameworks": ["React", "Node.js"],
        "technologies": ["Docker", "AWS"],
    })
    assert response.status_code == 201
    data = response.json()
    assert len(data["languages"]) == 2
    assert "Python" in data["languages"]
    assert len(data["frameworks"]) == 2
    assert "React" in data["frameworks"]
    assert len(data["technologies"]) == 2
    assert "Docker" in data["technologies"]

    # Cleanup
    await client.delete(f"/api/projects/{data['id']}")


async def test_project_bullet_points_order(client: AsyncClient):
    """Test that bullet points maintain their order."""
    response = await client.post("/api/projects", json={
        "title": "Bullet Order",
        "start_month": 1,
        "start_year": 2025,
        "bullet_points": ["First", "Second", "Third"],
    })
    assert response.status_code == 201
    data = response.json()
    assert data["bullet_points"] == ["First", "Second", "Third"]

    # Cleanup
    await client.delete(f"/api/projects/{data['id']}")


async def test_update_project_clears_old_tags(client: AsyncClient):
    """Test that updating a project's tags replaces old ones."""
    resp = await client.post("/api/projects", json={
        "title": "Tag Replace",
        "start_month": 1,
        "start_year": 2024,
        "tags": ["old-tag"],
    })
    pid = resp.json()["id"]

    resp2 = await client.put(f"/api/projects/{pid}", json={
        "tags": ["new-tag"],
    })
    assert resp2.status_code == 200
    assert resp2.json()["tags"] == ["new-tag"]

    # Cleanup
    await client.delete(f"/api/projects/{pid}")


async def test_update_project_partial(client: AsyncClient):
    """Test partial update of a project (only send one field)."""
    resp = await client.post("/api/projects", json={
        "title": "Partial Update",
        "start_month": 1,
        "start_year": 2024,
        "languages": ["Python"],
        "frameworks": ["Django"],
        "technologies": ["PostgreSQL"],
    })
    pid = resp.json()["id"]

    resp2 = await client.put(f"/api/projects/{pid}", json={
        "title": "Partially Updated",
    })
    assert resp2.status_code == 200
    data = resp2.json()
    assert data["title"] == "Partially Updated"
    # All three categories should still exist
    assert "Python" in data["languages"]
    assert "Django" in data["frameworks"]
    assert "PostgreSQL" in data["technologies"]

    # Cleanup
    await client.delete(f"/api/projects/{pid}")


async def test_seed_populates_projects(client: AsyncClient):
    """Test that seeding populates projects from fallback resume data."""
    import os
    from app.routes.projects import _seed_default_projects

    # Ensure no Google Doc ID is set so it uses fallback data
    os.environ.pop("GOOGLE_DOCS_ID", None)

    # Run seed on empty database
    _seed_default_projects()

    # Verify projects were created from fallback resume data
    list_resp = await client.get("/api/projects")
    projects = list_resp.json()
    assert len(projects) > 0
    # The fallback has a project called "Resume Website"
    titles = [p["title"] for p in projects]
    assert any("Resume" in t for t in titles) or any("Project" in t for t in titles)

    # Cleanup all seeded projects
    for p in projects:
        await client.delete(f"/api/projects/{p['id']}")


async def test_seed_skip_when_projects_exist(client: AsyncClient):
    """Test that seeding does nothing when projects already exist."""
    from app.routes.projects import _seed_default_projects

    # Create a project first
    resp = await client.post("/api/projects", json={
        "title": "Existing Project",
        "start_month": 6,
        "start_year": 2025,
    })
    pid = resp.json()["id"]

    # Run seed — should skip since projects exist
    _seed_default_projects()

    # Verify only one project remains (seed didn't add more)
    list_resp = await client.get("/api/projects")
    titles = [p["title"] for p in list_resp.json()]
    assert "Existing Project" in titles

    # Cleanup
    await client.delete(f"/api/projects/{pid}")
