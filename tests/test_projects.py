from conftest import create_project, add_place


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------

def test_create_project_minimal(client):
    r = client.post("/api/v1/projects", json={"name": "My Trip"})
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == "My Trip"
    assert data["status"] == "active"
    assert data["places"] == []


def test_create_project_full(client):
    r = client.post("/api/v1/projects", json={
        "name": "Chicago Tour",
        "description": "Art museums",
        "start_date": "2024-09-01",
    })
    assert r.status_code == 201
    data = r.json()
    assert data["description"] == "Art museums"
    assert data["start_date"] == "2024-09-01"


def test_create_project_with_places(client):
    """Project + places in one request."""
    r = client.post("/api/v1/projects", json={
        "name": "Trip",
        "places": [{"external_id": 27992}, {"external_id": 28560}],
    })
    assert r.status_code == 201
    data = r.json()
    assert len(data["places"]) == 2
    assert data["places"][0]["title"] == "A Sunday on La Grande Jatte — 1884"


def test_create_project_missing_name(client):
    r = client.post("/api/v1/projects", json={})
    assert r.status_code == 422


def test_create_project_empty_name(client):
    r = client.post("/api/v1/projects", json={"name": ""})
    assert r.status_code == 422


# ---------------------------------------------------------------------------
# Read
# ---------------------------------------------------------------------------

def test_get_project(client):
    project = create_project(client, "Trip")
    r = client.get(f"/api/v1/projects/{project['id']}")
    assert r.status_code == 200
    assert r.json()["name"] == "Trip"


def test_get_project_not_found(client):
    r = client.get("/api/v1/projects/999")
    assert r.status_code == 404


def test_list_projects(client):
    create_project(client, "Trip 1")
    create_project(client, "Trip 2")
    r = client.get("/api/v1/projects")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2


def test_list_projects_pagination(client):
    for i in range(5):
        create_project(client, f"Trip {i}")
    r = client.get("/api/v1/projects?page=1&limit=3")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 5
    assert len(data["items"]) == 3


def test_list_projects_filter_by_status(client):
    create_project(client, "Active Trip")
    r = client.get("/api/v1/projects?status=active")
    assert r.status_code == 200
    assert r.json()["total"] == 1


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------

def test_update_project(client):
    project = create_project(client, "Old Name")
    r = client.patch(f"/api/v1/projects/{project['id']}", json={"name": "New Name"})
    assert r.status_code == 200
    assert r.json()["name"] == "New Name"


def test_update_project_not_found(client):
    r = client.patch("/api/v1/projects/999", json={"name": "X"})
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------

def test_delete_project(client):
    project = create_project(client)
    r = client.delete(f"/api/v1/projects/{project['id']}")
    assert r.status_code == 204

    r = client.get(f"/api/v1/projects/{project['id']}")
    assert r.status_code == 404


def test_delete_project_with_visited_place(client):
    """Cannot delete a project that has at least one visited place."""
    project = create_project(client)
    place = add_place(client, project["id"], 27992).json()

    client.patch(
        f"/api/v1/projects/{project['id']}/places/{place['id']}",
        json={"visited": True},
    )

    r = client.delete(f"/api/v1/projects/{project['id']}")
    assert r.status_code == 409


def test_delete_project_not_found(client):
    r = client.delete("/api/v1/projects/999")
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# Auto-complete
# ---------------------------------------------------------------------------

def test_project_auto_completes_when_all_places_visited(client):
    """When all places are visited the project status becomes completed."""
    project = create_project(client)
    place = add_place(client, project["id"], 27992).json()

    client.patch(
        f"/api/v1/projects/{project['id']}/places/{place['id']}",
        json={"visited": True},
    )

    r = client.get(f"/api/v1/projects/{project['id']}")
    assert r.json()["status"] == "completed"


def test_project_stays_active_if_not_all_visited(client):
    project = create_project(client)
    place1 = add_place(client, project["id"], 27992).json()
    add_place(client, project["id"], 28560)

    client.patch(
        f"/api/v1/projects/{project['id']}/places/{place1['id']}",
        json={"visited": True},
    )

    r = client.get(f"/api/v1/projects/{project['id']}")
    assert r.json()["status"] == "active"