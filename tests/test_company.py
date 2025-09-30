from fastapi.testclient import TestClient
from uuid import uuid4
import random
import string

from app.main import app
from app.models.company import Company
from app.core.database import LocalSession

COMPANY_URL = "/companies"
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

def test_get_admin_company():
    token = get_admin_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get my company
    response = client.get(f"{COMPANY_URL}/me", headers=headers)

    assert response.status_code == 200
    data = response.json()

    assert data["name"] == "MyCompany"
    assert data["description"] == "MyCompanyDescription"

def test_get_non_admin_company():
    token = get_non_admin_token()

    headers = {"Authorization": f"Bearer {token}"}
    # Get my company
    response = client.get(f"{COMPANY_URL}/me", headers=headers)

    assert response.status_code == 200
    data = response.json()

    assert data["name"] == "MyCompany"
    assert data["description"] == "MyCompanyDescription"

def test_get_company_by_id():
    token = get_admin_token()

    headers = {"Authorization": f"Bearer {token}"}
    # Get my company
    response = client.get(f"{COMPANY_URL}/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    company_id = data["id"]

    # Get company by id
    response = client.get(f"{COMPANY_URL}/{company_id}", headers=headers)
    assert response.status_code == 200
    data_by_id = response.json()

    assert data == data_by_id

def test_update_company():
    current_company_name = "MyCompany"
    current_company_desc = "MyCompanyDescription"
    new_name = "UpdatedCompanyName"
    new_address = "UpdatedCompanyAddress"

    token = get_admin_token()

    headers = {"Authorization": f"Bearer {token}"}
    # Get my company
    response = client.get(f"{COMPANY_URL}/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    company_id = data["id"]

    # Update company
    response = client.put(
        f"{COMPANY_URL}/{company_id}",
        json={"name": new_name, "description": new_address},
        headers=headers,
    )
    assert response.status_code == 200
    updated_data = response.json()

    assert updated_data["name"] == new_name
    assert updated_data["description"] == new_address

    # Revert changes
    client.put(
        f"{COMPANY_URL}/{company_id}",
        json={"name": current_company_name, "description": current_company_desc},
        headers=headers,
    )

def test_create_company():
    token = get_admin_token()

    headers = {"Authorization": f"Bearer {token}"}
    new_company_name = radom_string(10)
    new_company_description = radom_string(20)
    
    # Create new company
    response = client.post(
        COMPANY_URL,
        json={"name": new_company_name, "description": new_company_description},
        headers=headers,
    )
    assert response.status_code == 201
    data = response.json()

    assert data["name"] == new_company_name
    assert data["description"] == new_company_description

    # Clean up - delete the created company directly from DB
    company_id = data["id"]
    with LocalSession() as db:
        company = db.get(Company, company_id)
        if company:
            db.delete(company)
            db.commit()

def test_get_company_by_id_not_found():
    token = get_admin_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Attempt to get a non-existing company by id
    non_existing_company_id = str(uuid4())

    response = client.get(f"{COMPANY_URL}/{non_existing_company_id}", headers=headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Company not found"

def test_non_admin_cannot_create_company():
    token = get_non_admin_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Attempt to create a company
    response = client.post(
        COMPANY_URL,
        json={"name": "ShouldNotCreate", "address": "NoAddress"},
        headers=headers,
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Admin only"

def test_create_company_missing_fields():
    token = get_admin_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Attempt to create a company with missing fields
    response = client.post(
        COMPANY_URL,
        json={"description": "IncompleteCompany"},
        headers=headers,
    )
    assert response.status_code == 422

def test_update_company_forbidden():
    token = get_non_admin_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Attempt to update a different company
    different_company_id = str(uuid4())
    response = client.put(
        f"{COMPANY_URL}/{different_company_id}",
        json={"name": "ShouldNotUpdate", "address": "NoAddress"},
        headers=headers,
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Not allowed across companies"

def test_update_company_non_admin_forbidden():
    token = get_non_admin_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Get user's company id
    response = client.get(f"{COMPANY_URL}/me", headers=headers)
    assert response.status_code == 200
    company_id = response.json()["id"]

    # Attempt to update own company as non-admin 
    response = client.put(
        f"{COMPANY_URL}/{company_id}",
        json={"name": "ShouldNotUpdate", "address": "NoAddress"},
        headers=headers,
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Admin only"