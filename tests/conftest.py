import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch

from main import app
from app.core.database import Base, get_db

# ---------------------------------------------------------------------------
# Test database — separate SQLite in memory, never touches real DB
# ---------------------------------------------------------------------------
TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Mock AIC API responses — no real HTTP calls during tests
# ---------------------------------------------------------------------------
MOCK_ARTWORK = {
    "external_id": 27992,
    "title": "A Sunday on La Grande Jatte — 1884",
    "artist": "Georges Seurat (French, 1859-1891)",
    "image_id": "2d484387-2509-5e8e-2c43-22f9981972eb",
}

MOCK_ARTWORK_2 = {
    "external_id": 28560,
    "title": "Nighthawks",
    "artist": "Edward Hopper (American, 1882-1967)",
    "image_id": "abc12345-0000-0000-0000-000000000000",
}


def mock_get_artwork(external_id: int):
    artworks = {
        27992: MOCK_ARTWORK,
        28560: MOCK_ARTWORK_2,
        **{i: {**MOCK_ARTWORK, "external_id": i, "title": f"Artwork {i}"} for i in range(1, 15)},
    }
    return artworks.get(external_id)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture(autouse=True)
def setup_database():
    """Create all tables before each test, drop after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    """FastAPI test client with overridden DB and mocked AIC API."""
    app.dependency_overrides[get_db] = override_get_db

    with patch("app.services.place_service.aic_client.get_artwork", side_effect=mock_get_artwork):
        with TestClient(app) as c:
            yield c

    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def create_project(client, name="Test Trip", places=None):
    payload = {"name": name}
    if places:
        payload["places"] = places
    r = client.post("/api/v1/projects", json=payload)
    assert r.status_code == 201
    return r.json()


def add_place(client, project_id, external_id):
    r = client.post(f"/api/v1/projects/{project_id}/places", json={"external_id": external_id})
    return r