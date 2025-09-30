from fastapi.testclient import TestClient
from uuid import uuid4
import random
import string

from app.main import app

USERS_URL = '/users'
TODOS_URL = '/todos'
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

def test_get_list_tasks():
    token = get_admin_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get task list
    response = client.get(TODOS_URL, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    for item in data:
        assert "id" in item
        assert "title" in item
        assert "content" in item
        assert "is_completed" in item
        assert "user_id" in item
        assert "company_id" in item
        assert "created_at" in item
        assert "updated_at" in item

def test_get_task_by_id():
    token = get_non_admin_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Get non admin profile
    response = client.get(f"{USERS_URL}/me", headers=headers)

    assert response.status_code == 200
    data = response.json()
    user_id = data["id"]
    company_id = data["company_id"]

    # Create a new task
    payload = {
        "title": "Test Task",
        "content": "This is a test task",
        "is_completed": False
    }

    response = client.post(TODOS_URL, json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    task_id = data["id"]

    # Get the created task by id
    response = client.get(f"{TODOS_URL}/{task_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == "Test Task"
    assert data["content"] == "This is a test task"
    assert data["is_completed"] == False
    assert data["user_id"] == user_id
    assert data["company_id"] == company_id

def test_create_task_as_admin():
    token = get_admin_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Get non admin profile
    response = client.get(f"{USERS_URL}/me", headers=headers)

    assert response.status_code == 200
    data = response.json()
    user_id = data["id"]
    company_id = data["company_id"]

    # Create a new task
    payload = {
        "title": "Test Task",
        "content": "This is a test task",
        "is_completed": False
    }

    response = client.post(TODOS_URL, json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["content"] == "This is a test task"
    assert data["is_completed"] == False
    assert data["user_id"] == user_id
    assert data["company_id"] == company_id

def test_create_task_as_non_admin():
    token = get_non_admin_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Get non admin profile
    response = client.get(f"{USERS_URL}/me", headers=headers)

    assert response.status_code == 200
    data = response.json()
    user_id = data["id"]
    company_id = data["company_id"]

    # Create a new task
    payload = {
        "title": "Test Task",
        "content": "This is a test task",
        "is_completed": False
    }

    response = client.post(TODOS_URL, json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["content"] == "This is a test task"
    assert data["is_completed"] == False
    assert data["user_id"] == user_id
    assert data["company_id"] == company_id

def test_update_task():
    token = get_non_admin_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Get non admin profile
    response = client.get(f"{USERS_URL}/me", headers=headers)

    assert response.status_code == 200
    data = response.json()
    user_id = data["id"]
    company_id = data["company_id"]

    # Create a new task
    payload = {
        "title": "Test Task",
        "content": "This is a test task",
        "is_completed": False
    }

    response = client.post(TODOS_URL, json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    task_id = data["id"]

    # Update the created task
    update_payload = {
        "title": "Updated Test Task",
        "content": "This is an updated test task",
        "is_completed": True
    }

    response = client.put(f"{TODOS_URL}/{task_id}", json=update_payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == "Updated Test Task"
    assert data["content"] == "This is an updated test task"
    assert data["is_completed"] == True
    assert data["user_id"] == user_id
    assert data["company_id"] == company_id

def test_update_task_not_found():
    token = get_non_admin_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Update a non-existing task
    non_existing_task_id = str(uuid4())
    update_payload = {
        "title": "Updated Test Task",
        "content": "This is an updated test task",
        "is_completed": True
    }

    response = client.put(f"{TODOS_URL}/{non_existing_task_id}", json=update_payload, headers=headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"

def test_delete_task():
    token = get_non_admin_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Get task list
    response = client.get(TODOS_URL, headers=headers)
    assert response.status_code == 200
    todo_list = response.json()
    assert isinstance(todo_list, list)
    print(todo_list)

    response = client.delete(f"{TODOS_URL}/{todo_list[0]["id"]}", headers=headers)
    assert response.status_code == 204

def test_delete_task_not_found():
    token = get_non_admin_token()
    headers = {"Authorization": f"Bearer {token}"}

    non_existing_task_id = str(uuid4())
    response = client.delete(f"{TODOS_URL}/{non_existing_task_id}", headers=headers)
    
    assert response.status_code == 404 
    assert response.json()["detail"] == "Task not found"