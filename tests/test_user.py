from uuid import uuid4
from .utils import random_string

USERS_URL = '/users'

def test_get_admin_profile(test_client, admin_headers):
    """Test that admin can get their profile information."""
    response = test_client.get(f"{USERS_URL}/me", headers=admin_headers)

    assert response.status_code == 200
    data = response.json()

    assert data["username"] == "admin"
    assert data["email"] == "admin@mycompany.com"
    assert data["is_admin"] == True
    assert data["is_active"] == True

def test_get_non_admin_profile(test_client, non_admin_headers):
    """Test that non-admin can get their profile information."""
    response = test_client.get(f"{USERS_URL}/me", headers=non_admin_headers)

    assert response.status_code == 200
    data = response.json()

    assert data["username"] == "khoi.vuongdinh"
    assert data["is_admin"] == False
    assert data["is_active"] == True

def test_get_user_by_id(test_client, non_admin_headers):
    """Test getting a user by ID returns correct user data."""
    test_user_id = "10111add-9140-45ef-ae7c-97c413a8dbdb"
    response = test_client.get(f"{USERS_URL}/{test_user_id}", headers=non_admin_headers)
    assert response.status_code == 200

    data = response.json()
    assert data["username"] == "testuser"
    assert data["is_admin"] == False
    assert data["is_active"] == True

def test_get_user_by_id_not_found(test_client, non_admin_headers):
    """Test that getting a non-existing user returns 404."""
    test_user_id = str(uuid4())
    response = test_client.get(f"{USERS_URL}/{test_user_id}", headers=non_admin_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"

def test_admin_create_user(test_client, admin_headers):
    """Test that admin can create a new user."""
    username = random_string(8)
    email = random_string(5) + "@test.com"
    first_name = random_string(10)
    last_name = random_string(10)
    password = random_string(8)
    payload = {
        "username": username,
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "password": password,
        "is_active": True,
        "is_admin": False
    }

    response = test_client.post(USERS_URL, json=payload, headers=admin_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == username
    assert data["email"] == email
    assert data["first_name"] == first_name
    assert data["last_name"] == last_name
    assert data["is_active"] == True
    assert data["is_admin"] == False

def test_non_admin_create_user_forbidden(test_client, non_admin_headers):
    """Test that non-admin users cannot create users."""
    username = random_string(8)
    email = random_string(5) + "@test.com"
    first_name = random_string(10)
    last_name = random_string(10)
    password = random_string(8)
    payload = {
        "username": username,
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "password": password,
        "is_active": True,
        "is_admin": False
    }

    response = test_client.post(USERS_URL, json=payload, headers=non_admin_headers)
    assert response.status_code == 403
    assert response.json()["detail"] == "Admin only"

def test_admin_update_user(test_client, admin_headers):
    """Test that admin can update user information."""
    test_user_id = "606621d3-0115-437d-b4f7-aeabf8f79aad"
    new_first_name = random_string(10)
    new_last_name = random_string(10)
    payload = {
        "first_name": new_first_name,
        "last_name": new_last_name,
        "is_active": False
    }

    response = test_client.put(f"{USERS_URL}/{test_user_id}", json=payload, headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == new_first_name
    assert data["last_name"] == new_last_name
    assert data["is_active"] == False

def test_non_admin_update_user_forbidden(test_client, non_admin_headers):
    """Test that non-admin users cannot update other users."""
    test_user_id = "606621d3-0115-437d-b4f7-aeabf8f79aad"
    new_first_name = random_string(10)
    new_last_name = random_string(10)
    payload = {
        "first_name": new_first_name,
        "last_name": new_last_name,
        "is_active": False
    }

    response = test_client.put(f"{USERS_URL}/{test_user_id}", json=payload, headers=non_admin_headers)
    assert response.status_code == 403
    assert response.json()["detail"] == "Not allowed"

def test_non_admin_update_basic_info(test_client, non_admin_headers):
    """Test that non-admin users can update their own basic information."""
    # Get user's id
    response = test_client.get(f"{USERS_URL}/me", headers=non_admin_headers)
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

    response = test_client.put(f"{USERS_URL}/{user_id}", json=payload, headers=non_admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == new_first_name
    assert data["last_name"] == new_last_name
    assert data["username"] == "khoi.vuongdinh"
    assert data["is_admin"] == False
    assert data["is_active"] == True

def test_delete_user_forbidden(test_client, non_admin_headers):
    """Test that non-admin users cannot delete users."""
    test_user_id = "10111add-9140-45ef-ae7c-97c413a8dbdb"

    response = test_client.delete(f"{USERS_URL}/{test_user_id}", headers=non_admin_headers)
    assert response.status_code == 403
    assert response.json()["detail"] == "Admin only"


def test_admin_delete_user(test_client, admin_headers):
    """Test that admin can delete users."""
    # Create user
    username = random_string(8)
    email = random_string(5) + "@test.com"
    first_name = random_string(10)
    last_name = random_string(10)
    password = random_string(8)
    payload = {
        "username": username,
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "password": password,
        "is_active": True,
        "is_admin": False
    }

    response = test_client.post(USERS_URL, json=payload, headers=admin_headers)
    assert response.status_code == 201
    user_id = response.json()["id"]

    # Delete user
    response = test_client.delete(f"{USERS_URL}/{user_id}", headers=admin_headers)
    assert response.status_code == 204
    # Verify user is deleted
    response = test_client.get(f"{USERS_URL}/{user_id}", headers=admin_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"
