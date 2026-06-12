from conftest import create_project, add_place


# ---------------------------------------------------------------------------
# Add place
# ---------------------------------------------------------------------------

def test_add_place(client):
    project = create_project(client)
    r = add_place(client, project["id"], 27992)
    assert r.status_code == 201
    data = r.json()
    assert data["external_id"] == 27992
    assert data["title"] == "A Sunday on La Grande Jatte — 1884"
    assert data["visited"] is False
    assert data["notes"] is None


def test_add_place_to_nonexistent_project(client):
    r = add_place(client, 999, 27992)
    assert r.status_code == 404


def test_add_duplicate_place(client):
    """Same artwork cannot be added twice to the same project."""
    project = create_project(client)
    add_place(client, project["id"], 27992)
    r = add_place(client, project["id"], 27992)
    assert r.status_code == 409


def test_add_nonexistent_artwork(client):
    """Artwork that doesn't exist in AIC API should return 404."""
    project = create_project(client)
    r = client.post(f"/api/v1/projects/{project['id']}/places", json={"external_id": 99999999})
    assert r.status_code == 404


def test_add_invalid_external_id(client):
    """external_id must be a positive integer."""
    project = create_project(client)
    r = client.post(f"/api/v1/projects/{project['id']}/places", json={"external_id": -1})
    assert r.status_code == 422


def test_max_places_per_project(client):
    """A project cannot have more than 10 places."""
    project = create_project(client)

    for i in range(1, 11):
        r = add_place(client, project["id"], i)
        assert r.status_code == 201

    # 11th place should be rejected
    r = add_place(client, project["id"], 11)
    assert r.status_code == 422


# ---------------------------------------------------------------------------
# Read
# ---------------------------------------------------------------------------

def test_get_place(client):
    project = create_project(client)
    place = add_place(client, project["id"], 27992).json()

    r = client.get(f"/api/v1/projects/{project['id']}/places/{place['id']}")
    assert r.status_code == 200
    assert r.json()["external_id"] == 27992


def test_get_place_not_found(client):
    project = create_project(client)
    r = client.get(f"/api/v1/projects/{project['id']}/places/999")
    assert r.status_code == 404


def test_list_places(client):
    project = create_project(client)
    add_place(client, project["id"], 27992)
    add_place(client, project["id"], 28560)

    r = client.get(f"/api/v1/projects/{project['id']}/places")
    assert r.status_code == 200
    assert len(r.json()) == 2


def test_list_places_empty(client):
    project = create_project(client)
    r = client.get(f"/api/v1/projects/{project['id']}/places")
    assert r.status_code == 200
    assert r.json() == []


# ---------------------------------------------------------------------------
# Update place
# ---------------------------------------------------------------------------

def test_update_notes(client):
    project = create_project(client)
    place = add_place(client, project["id"], 27992).json()

    r = client.patch(
        f"/api/v1/projects/{project['id']}/places/{place['id']}",
        json={"notes": "Amazing painting!"},
    )
    assert r.status_code == 200
    assert r.json()["notes"] == "Amazing painting!"


def test_mark_as_visited(client):
    project = create_project(client)
    place = add_place(client, project["id"], 27992).json()

    r = client.patch(
        f"/api/v1/projects/{project['id']}/places/{place['id']}",
        json={"visited": True},
    )
    assert r.status_code == 200
    assert r.json()["visited"] is True


def test_update_notes_and_visited_together(client):
    project = create_project(client)
    place = add_place(client, project["id"], 27992).json()

    r = client.patch(
        f"/api/v1/projects/{project['id']}/places/{place['id']}",
        json={"notes": "Great!", "visited": True},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["notes"] == "Great!"
    assert data["visited"] is True


def test_update_place_not_found(client):
    project = create_project(client)
    r = client.patch(
        f"/api/v1/projects/{project['id']}/places/999",
        json={"visited": True},
    )
    assert r.status_code == 404


def test_place_belongs_to_project(client):
    """Place from project A cannot be accessed via project B."""
    project_a = create_project(client, "Project A")
    project_b = create_project(client, "Project B")
    place = add_place(client, project_a["id"], 27992).json()

    r = client.get(f"/api/v1/projects/{project_b['id']}/places/{place['id']}")
    assert r.status_code == 404