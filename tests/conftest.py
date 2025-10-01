from fastapi.testclient import TestClient
from app.main import app
import pytest

client = TestClient(app)

AUTH_URL = "/auth/login"

@pytest.fixture
def test_client():
  with TestClient(app) as client:
    yield client

# Setup: create a test database session
@pytest.fixture(scope="module")
def test_db():
    from app.core.database import LocalSession, Base, engine
    Base.metadata.create_all(bind=engine)
    db = LocalSession()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)

# Token admin / non-admin
@pytest.fixture
def admin_token(test_client):
    resp = test_client.post(AUTH_URL, data={"username": "admin", "password": "admin@123"})
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]

@pytest.fixture
def non_admin_token(test_client):
    resp = test_client.post(AUTH_URL, data={"username": "khoi.vuongdinh", "password": "Kh@ivuong3101"})
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]

# Header
@pytest.fixture
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}

@pytest.fixture
def non_admin_headers(non_admin_token):
    return {"Authorization": f"Bearer {non_admin_token}"}