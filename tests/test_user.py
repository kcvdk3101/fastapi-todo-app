from fastapi.testclient import TestClient
from uuid import uuid4
import random
import string

from app.main import app

USERS_URL = '/users'
AUTH_URL = "/auth/login"


client = TestClient(app)

def get_admin_token():
    response = client.post(AUTH_URL, data={"username": "admin", "password": "admin@123"})
    assert response.status_code == 200
    token = response.json()["access_token"]
    return token

def get_non_admin_token():
    response = client.post(AUTH_URL, data={"username": "khoi.vuongdinh", "password": "Kh@ivuong3101"})
    assert response.status_code == 200
    token = response.json()["access_token"]
    return token

def radom_string(length=8):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(length))

def test_get_admin_profile():
    token = get_admin_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get admin profile
    response = client.get(f"{USERS_URL}/me", headers=headers)

    assert response.status_code == 200
    data = response.json()

    assert data["username"] == "admin"
    assert data["email"] == "admin@mycompany.com"
    assert data["is_admin"] == True
    assert data["is_active"] == True

def test_get_non_admin_profile():
    token = get_non_admin_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get non admin profile
    response = client.get(f"{USERS_URL}/me", headers=headers)

    assert response.status_code == 200
    data = response.json()

    assert data["username"] == "khoi.vuongdinh"
    assert data["is_admin"] == False
    assert data["is_active"] == True

def test_get_user_by_id():
    token = get_non_admin_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get user by id
    test_user_id = "10111add-9140-45ef-ae7c-97c413a8dbdb"
    response = client.get(f"{USERS_URL}/{test_user_id}", headers=headers)
    assert response.status_code == 200

    data = response.json()
    assert data["username"] == "testuser"
    assert data["is_admin"] == False
    assert data["is_active"] == True

def test_get_user_by_id_not_found():
    token = get_non_admin_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get user by id
    test_user_id = str(uuid4())
    response = client.get(f"{USERS_URL}/{test_user_id}", headers=headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"

def test_admin_create_user():
    token = get_admin_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create user
    username = radom_string(8)
    email = radom_string(5)+"@test.com"
    first_name = radom_string(10)
    last_name = radom_string(10)
    password = radom_string(8)
    payload = {
        "username": username,
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "password": password,
        "is_active": True,
        "is_admin": False
    }

    response = client.post(USERS_URL, json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == username
    assert data["email"] == email
    assert data["first_name"] == first_name
    assert data["last_name"] == last_name
    assert data["is_active"] == True
    assert data["is_admin"] == False

def test_non_admin_create_user_forbidden():
    token = get_non_admin_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create user
    username = radom_string(8)
    email = radom_string(5)+"@test.com"
    first_name = radom_string(10)
    last_name = radom_string(10)
    password = radom_string(8)
    payload = {
        "username": username,
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "password": password,
        "is_active": True,
        "is_admin": False
    }

    response = client.post(USERS_URL, json=payload, headers=headers)
    assert response.status_code == 403
    assert response.json()["detail"] == "Admin only"

def test_admin_update_user():
    token = get_admin_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Update user
    test_user_id = "606621d3-0115-437d-b4f7-aeabf8f79aad"
    new_first_name = radom_string(10)
    new_last_name = radom_string(10)
    payload = {
        "first_name": new_first_name,
        "last_name": new_last_name,
        "is_active": False
    }

    response = client.put(f"{USERS_URL}/{test_user_id}", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == new_first_name
    assert data["last_name"] == new_last_name
    assert data["is_active"] == False

def test_non_admin_update_user_forbidden():
    token = get_non_admin_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Update user
    test_user_id = "606621d3-0115-437d-b4f7-aeabf8f79aad"
    new_first_name = radom_string(10)
    new_last_name = radom_string(10)
    payload = {
        "first_name": new_first_name,
        "last_name": new_last_name,
        "is_active": False
    }

    response = client.put(f"{USERS_URL}/{test_user_id}", json=payload, headers=headers)
    assert response.status_code == 403
    assert response.json()["detail"] == "Not allowed"

def test_non_admin_update_basic_info():
    token = get_non_admin_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Get user's id
    response = client.get(f"{USERS_URL}/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    user_id = data["id"]

    # Update own basic info
    new_first_name = "Khoi"
    new_last_name = "Vuong"
    payload = {
        "first_name": new_first_name,
        "last_name": new_last_name,
    }

    response = client.put(f"{USERS_URL}/{user_id}", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == new_first_name
    assert data["last_name"] == new_last_name
    assert data["username"] == "khoi.vuongdinh"
    assert data["is_admin"] == False
    assert data["is_active"] == True

def test_delete_user_forbidden():
    token = get_non_admin_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Delete user
    test_user_id = "10111add-9140-45ef-ae7c-97c413a8dbdb"

    response = client.delete(f"{USERS_URL}/{test_user_id}", headers=headers)
    assert response.status_code == 403
    assert response.json()["detail"] == "Admin only"

def test_admin_delete_user():
    token = get_admin_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Create user
    username = radom_string(8)
    email = radom_string(5)+"@test.com"
    first_name = radom_string(10)
    last_name = radom_string(10)
    password = radom_string(8)
    payload = {
        "username": username,
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "password": password,
        "is_active": True,
        "is_admin": False
    }

    response = client.post(USERS_URL, json=payload, headers=headers)
    assert response.status_code == 201
    user_id = response.json()["id"]

    # Delete user
    response = client.delete(f"{USERS_URL}/{user_id}", headers=headers)
    assert response.status_code == 204
    # Verify user is deleted
    response = client.get(f"{USERS_URL}/{user_id}", headers=headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"
