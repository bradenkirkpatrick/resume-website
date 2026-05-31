"""Tests for person, education, and experiences endpoints."""
from httpx import AsyncClient


async def test_create_person(client: AsyncClient):
    resp = await client.post("/api/person", json={"name": "Braden", "email": "b@b.com"})
    assert resp.status_code == 201
    d = resp.json()
    assert d["name"] == "Braden"
    assert d["email"] == "b@b.com"
    assert "person_id" in d


async def test_list_persons(client: AsyncClient):
    await client.post("/api/person", json={"name": "A"})
    await client.post("/api/person", json={"name": "B"})
    resp = await client.get("/api/person")
    assert len(resp.json()) == 2


async def test_get_person(client: AsyncClient):
    cr = await client.post("/api/person", json={"name": "Test"})
    pid = cr.json()["person_id"]
    resp = await client.get(f"/api/person/{pid}")
    assert resp.json()["name"] == "Test"


async def test_update_person(client: AsyncClient):
    cr = await client.post("/api/person", json={"name": "Old"})
    pid = cr.json()["person_id"]
    resp = await client.put(f"/api/person/{pid}", json={"name": "New"})
    assert resp.json()["name"] == "New"


async def test_delete_person(client: AsyncClient):
    cr = await client.post("/api/person", json={"name": "Del"})
    pid = cr.json()["person_id"]
    assert (await client.delete(f"/api/person/{pid}")).status_code == 204
    assert (await client.get(f"/api/person/{pid}")).status_code == 404


async def test_create_education(client: AsyncClient):
    pr = await client.post("/api/person", json={"name": "Test"})
    pid = pr.json()["person_id"]
    resp = await client.post("/api/education", json={
        "person_id": pid, "school": "MIT", "degree": "BS",
    })
    assert resp.status_code == 201
    assert resp.json()["school"] == "MIT"


async def test_create_experience(client: AsyncClient):
    pr = await client.post("/api/person", json={"name": "Test"})
    pid = pr.json()["person_id"]
    resp = await client.post("/api/experiences", json={
        "person_id": pid, "company": "Google", "role": "Engineer",
    })
    assert resp.status_code == 201
    assert resp.json()["company"] == "Google"


async def test_update_education(client: AsyncClient):
    pr = await client.post("/api/person", json={"name": "T"})
    pid = pr.json()["person_id"]
    cr = await client.post("/api/education", json={
        "person_id": pid, "school": "MIT", "degree": "BS",
    })
    eid = cr.json()["id"]
    resp = await client.put(f"/api/education/{eid}", json={"degree": "MS"})
    assert resp.json()["degree"] == "MS"


async def test_update_experience(client: AsyncClient):
    pr = await client.post("/api/person", json={"name": "T"})
    pid = pr.json()["person_id"]
    cr = await client.post("/api/experiences", json={
        "person_id": pid, "company": "G", "role": "Dev",
    })
    eid = cr.json()["id"]
    resp = await client.put(f"/api/experiences/{eid}", json={"role": "Senior"})
    assert resp.json()["role"] == "Senior"


async def test_list_education_by_person(client: AsyncClient):
    pr = await client.post("/api/person", json={"name": "T"})
    pid = pr.json()["person_id"]
    await client.post("/api/education", json={"person_id": pid, "school": "A"})
    await client.post("/api/education", json={"person_id": pid, "school": "B"})
    resp = await client.get(f"/api/education?person_id={pid}")
    assert len(resp.json()) == 2


async def test_list_experiences_by_person(client: AsyncClient):
    pr = await client.post("/api/person", json={"name": "T"})
    pid = pr.json()["person_id"]
    await client.post("/api/experiences", json={"person_id": pid, "company": "A"})
    await client.post("/api/experiences", json={"person_id": pid, "company": "B"})
    resp = await client.get(f"/api/experiences?person_id={pid}")
    assert len(resp.json()) == 2
