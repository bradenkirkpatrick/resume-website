"""
Tests for the normalized project management API endpoints.
"""

from httpx import AsyncClient


PERSON = {"name": "Test User", "email": "test@example.com"}


async def _create_person(client: AsyncClient) -> int:
    resp = await client.post("/api/person", json=PERSON)
    return resp.json()["person_id"]


async def test_list_projects_empty(client: AsyncClient):
    pid = await _create_person(client)
    resp = await client.get(f"/api/projects?person_id={pid}")
    assert resp.status_code == 200
    assert resp.json() == []


async def test_create_project_minimal(client: AsyncClient):
    pid = await _create_person(client)
    resp = await client.post("/api/projects", json={
        "person_id": pid, "project_name": "Test Project",
    })
    assert resp.status_code == 201
    d = resp.json()
    assert d["project_name"] == "Test Project"
    assert d["bullet_points"] == []
    assert d["technologies"] == []


async def test_create_project_full(client: AsyncClient):
    pid = await _create_person(client)
    resp = await client.post("/api/projects", json={
        "person_id": pid, "project_name": "Full Stack App",
        "project_role": "Lead Dev",
        "start_date": "2023-03-01",
        "end_date": "2024-06-01",
        "languages": ["Python", "TypeScript"],
        "frameworks": ["React", "FastAPI"],
        "technologies": ["Docker"],
        "bullet_points": ["Built frontend", "Designed API"],
    })
    assert resp.status_code == 201
    d = resp.json()
    assert d["project_name"] == "Full Stack App"
    assert "Python" in d["languages"]
    assert "React" in d["frameworks"]
    assert "Docker" in d["technologies"]
    assert len(d["bullet_points"]) == 2


async def test_get_project(client: AsyncClient):
    pid = await _create_person(client)
    cr = await client.post("/api/projects", json={
        "person_id": pid, "project_name": "Get Test",
    })
    proj_id = cr.json()["id"]
    resp = await client.get(f"/api/projects/{proj_id}")
    assert resp.status_code == 200
    assert resp.json()["project_name"] == "Get Test"


async def test_get_project_not_found(client: AsyncClient):
    assert (await client.get("/api/projects/99999")).status_code == 404


async def test_list_projects_after_create(client: AsyncClient):
    pid = await _create_person(client)
    await client.post("/api/projects", json={"person_id": pid, "project_name": "A"})
    await client.post("/api/projects", json={"person_id": pid, "project_name": "B"})
    resp = await client.get(f"/api/projects?person_id={pid}")
    assert len(resp.json()) == 2


async def test_update_project(client: AsyncClient):
    pid = await _create_person(client)
    cr = await client.post("/api/projects", json={
        "person_id": pid, "project_name": "Original",
    })
    proj_id = cr.json()["id"]
    resp = await client.put(f"/api/projects/{proj_id}", json={
        "project_name": "Updated", "technologies": ["Docker"],
    })
    assert resp.status_code == 200
    assert resp.json()["project_name"] == "Updated"
    assert "Docker" in resp.json()["technologies"]


async def test_update_project_not_found(client: AsyncClient):
    assert (await client.put("/api/projects/99999", json={"project_name": "Nope"})).status_code == 404


async def test_delete_project(client: AsyncClient):
    pid = await _create_person(client)
    cr = await client.post("/api/projects", json={
        "person_id": pid, "project_name": "Delete Me",
    })
    proj_id = cr.json()["id"]
    assert (await client.delete(f"/api/projects/{proj_id}")).status_code == 204
    assert (await client.get(f"/api/projects/{proj_id}")).status_code == 404


async def test_delete_project_not_found(client: AsyncClient):
    assert (await client.delete("/api/projects/99999")).status_code == 404


async def test_query_technologies(client: AsyncClient):
    pid = await _create_person(client)
    await client.post("/api/projects", json={
        "person_id": pid, "project_name": "P1", "technologies": ["Docker", "Python"],
    })
    await client.post("/api/projects", json={
        "person_id": pid, "project_name": "P2", "technologies": ["Python", "AWS"],
    })
    resp = await client.get("/api/projects/tech/all")
    assert resp.status_code == 200
    data = resp.json()
    assert "Docker" in data and "Python" in data and "AWS" in data


async def test_query_languages(client: AsyncClient):
    pid = await _create_person(client)
    await client.post("/api/projects", json={
        "person_id": pid, "project_name": "P1", "languages": ["Python", "JS"],
    })
    assert "Python" in (await client.get("/api/projects/languages/all")).json()


async def test_query_frameworks(client: AsyncClient):
    pid = await _create_person(client)
    await client.post("/api/projects", json={
        "person_id": pid, "project_name": "P1", "frameworks": ["React"],
    })
    assert "React" in (await client.get("/api/projects/frameworks/all")).json()


async def test_partial_update_preserves_categories(client: AsyncClient):
    pid = await _create_person(client)
    cr = await client.post("/api/projects", json={
        "person_id": pid, "project_name": "Partial",
        "languages": ["Python"], "frameworks": ["Django"], "technologies": ["PG"],
    })
    proj_id = cr.json()["id"]
    await client.put(f"/api/projects/{proj_id}", json={"project_name": "Updated"})
    d = (await client.get(f"/api/projects/{proj_id}")).json()
    assert d["project_name"] == "Updated"
    assert "Python" in d["languages"]
    assert "Django" in d["frameworks"]
    assert "PG" in d["technologies"]
