from uuid import uuid4

USERS_URL = '/users'
TODOS_URL = '/todos'

def test_get_list_tasks_admin(test_client, admin_headers):
    """Admin can retrieve list of tasks."""
    response = test_client.get(TODOS_URL, headers=admin_headers)
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

def test_get_list_tasks_non_admin(test_client, non_admin_headers):
    """Non-admin can retrieve list of tasks."""
    response = test_client.get(TODOS_URL, headers=non_admin_headers)
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

def test_get_task_by_id(test_client, non_admin_headers):
    """Non-admin can get their created task by id."""
    # Get non admin profile
    response = test_client.get(f"{USERS_URL}/me", headers=non_admin_headers)

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

    response = test_client.post(TODOS_URL, json=payload, headers=non_admin_headers)
    assert response.status_code == 201
    data = response.json()
    task_id = data["id"]

    # Get the created task by id
    response = test_client.get(f"{TODOS_URL}/{task_id}", headers=non_admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == "Test Task"
    assert data["content"] == "This is a test task"
    assert data["is_completed"] == False
    assert data["user_id"] == user_id
    assert data["company_id"] == company_id

def test_create_task_as_admin(test_client, admin_headers):
    """Admin can create a task for themselves."""
    response = test_client.get(f"{USERS_URL}/me", headers=admin_headers)

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

    response = test_client.post(TODOS_URL, json=payload, headers=admin_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["content"] == "This is a test task"
    assert data["is_completed"] == False
    assert data["user_id"] == user_id
    assert data["company_id"] == company_id

def test_create_task_as_non_admin(test_client, non_admin_headers):
    """Non-admin can create a task for themselves."""
    response = test_client.get(f"{USERS_URL}/me", headers=non_admin_headers)

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

    response = test_client.post(TODOS_URL, json=payload, headers=non_admin_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["content"] == "This is a test task"
    assert data["is_completed"] == False
    assert data["user_id"] == user_id
    assert data["company_id"] == company_id

def test_update_task(test_client, non_admin_headers):
    """Non-admin can update their own task."""
    # Get non admin profile
    response = test_client.get(f"{USERS_URL}/me", headers=non_admin_headers)

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

    response = test_client.post(TODOS_URL, json=payload, headers=non_admin_headers)
    assert response.status_code == 201
    data = response.json()
    task_id = data["id"]

    # Update the created task
    update_payload = {
        "title": "Updated Test Task",
        "content": "This is an updated test task",
        "is_completed": True
    }

    response = test_client.put(f"{TODOS_URL}/{task_id}", json=update_payload, headers=non_admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == "Updated Test Task"
    assert data["content"] == "This is an updated test task"
    assert data["is_completed"] == True
    assert data["user_id"] == user_id
    assert data["company_id"] == company_id

def test_update_task_not_found(test_client, non_admin_headers):
    """Updating a non-existing task should return 404."""
    non_existing_task_id = str(uuid4())
    update_payload = {
        "title": "Updated Test Task",
        "content": "This is an updated test task",
        "is_completed": True
    }

    response = test_client.put(
        f"{TODOS_URL}/{non_existing_task_id}", json=update_payload, headers=non_admin_headers
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"

def test_delete_task(test_client, non_admin_headers):
    """Non-admin can delete their own task."""
    # Create a task to delete
    payload = {
        "title": "Task To Delete",
        "content": "This task will be deleted",
        "is_completed": False
    }
    response = test_client.post(TODOS_URL, json=payload, headers=non_admin_headers)
    assert response.status_code == 201
    task_id = response.json()["id"]

    # Delete the task
    response = test_client.delete(f"{TODOS_URL}/{task_id}", headers=non_admin_headers)
    assert response.status_code == 204

    # Verify task is deleted
    response = test_client.get(f"{TODOS_URL}/{task_id}", headers=non_admin_headers)
    assert response.status_code == 404

def test_delete_task_not_found(test_client, non_admin_headers):
    """Deleting a non-existing task should return 404."""
    non_existing_task_id = str(uuid4())
    response = test_client.delete(f"{TODOS_URL}/{non_existing_task_id}", headers=non_admin_headers)
    
    assert response.status_code == 404 
    assert response.json()["detail"] == "Task not found"