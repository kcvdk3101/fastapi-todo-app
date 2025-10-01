from .conftest import AUTH_URL

def test_login_success(test_client):
    data = {"username": "admin", "password": "admin@123"}
    response = test_client.post(AUTH_URL, data=data)

    assert response.status_code == 200
    json_response = response.json()
    assert "access_token" in json_response
    assert json_response["token_type"] == "bearer"

def test_login_invalid_username(test_client):
    data = {"username": "wrongadmin", "password": "admin@123"}
    response = test_client.post(AUTH_URL, data=data)

    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect credentials"}

def test_login_invalid_password(test_client):
    data = {"username": "admin", "password": "wrongpass"}
    response = test_client.post(AUTH_URL, data=data)
    
    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect credentials"}