from fastapi.testclient import TestClient
from app.main import app

AUTH_URL = "/login"

client = TestClient(app)

def test_login_success():
    response = client.post("/auth/login", data={"username": "admin", "password": "admin@123"})
    assert response.status_code == 200
    json_response = response.json()
    assert "access_token" in json_response
    assert json_response["token_type"] == "bearer"

def test_login_invalid_username():
    response = client.post("/auth/login", data={"username": "wrongadmin", "password": "admin@123"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect credentials"}

def test_login_invalid_password():
    response = client.post("/auth/login", data={"username": "admin", "password": "wrongpass"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect credentials"}