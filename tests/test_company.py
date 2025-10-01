from uuid import uuid4

from app.models.company import Company
from app.core.database import LocalSession
from .utils import random_string

COMPANY_URL = "/companies"

def test_get_admin_company(test_client, admin_headers):
    """Test that admin can get their company information."""
    expected_company_name = "MyCompany"
    expected_company_desc = "MyCompanyDescription"

    response = test_client.get(f"{COMPANY_URL}/me", headers=admin_headers)

    assert response.status_code == 200
    data = response.json()

    assert data["name"] == expected_company_name
    assert data["description"] == expected_company_desc


def test_get_non_admin_company(test_client, non_admin_headers):
    """Test that non-admin can get their company information."""
    expected_company_name = "MyCompany"
    expected_company_desc = "MyCompanyDescription"

    response = test_client.get(f"{COMPANY_URL}/me", headers=non_admin_headers)

    assert response.status_code == 200
    data = response.json()

    assert data["name"] == expected_company_name
    assert data["description"] == expected_company_desc

def test_get_company_by_id(test_client, admin_headers):
    """Test getting company by ID returns the same data as /me endpoint."""
    # Get my company
    response = test_client.get(f"{COMPANY_URL}/me", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    company_id = data["id"]

    # Get company by id
    response = test_client.get(f"{COMPANY_URL}/{company_id}", headers=admin_headers)
    assert response.status_code == 200
    data_by_id = response.json()

    assert data == data_by_id

def test_update_company(test_client, admin_headers):
    """Test that admin can update company information."""
    current_company_name = "MyCompany"
    current_company_desc = "MyCompanyDescription"
    new_name = "UpdatedCompanyName"
    new_address = "UpdatedCompanyAddress"

    # Get my company
    response = test_client.get(f"{COMPANY_URL}/me", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    company_id = data["id"]

    # Update company
    response = test_client.put(
        f"{COMPANY_URL}/{company_id}",
        json={"name": new_name, "description": new_address},
        headers=admin_headers,
    )
    assert response.status_code == 200
    updated_data = response.json()

    assert updated_data["name"] == new_name
    assert updated_data["description"] == new_address

    # Revert changes
    test_client.put(
        f"{COMPANY_URL}/{company_id}",
        json={"name": current_company_name, "description": current_company_desc},
        headers=admin_headers,
    )

def test_create_company(test_client, admin_headers):
    """Test that admin can create a new company."""
    new_company_name = random_string(10)
    new_company_description = random_string(20)
    
    # Create new company
    response = test_client.post(
        COMPANY_URL,
        json={"name": new_company_name, "description": new_company_description},
        headers=admin_headers,
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

def test_get_company_by_id_not_found(test_client, admin_headers):
    """Test that getting a non-existing company returns 404."""
    non_existing_company_id = str(uuid4())
    response = test_client.get(f"{COMPANY_URL}/{non_existing_company_id}", headers=admin_headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Company not found"

def test_non_admin_cannot_create_company(test_client, non_admin_headers):
    """Test that non-admin users cannot create companies."""
    payload = {"name": "ShouldNotCreate", "description": "NoneDescription"}

    response = test_client.post(
        COMPANY_URL,
        json=payload,
        headers=non_admin_headers,
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Admin only"

def test_create_company_missing_fields(test_client, admin_headers):
    """Test that creating a company with missing required fields returns 422."""
    response = test_client.post(
        COMPANY_URL,
        json={"description": "IncompleteCompany"},
        headers=admin_headers,
    )

    assert response.status_code == 422

def test_update_company_forbidden(test_client, non_admin_headers):
    """Test that non-admin users cannot update other companies."""
    payload = {"name": "ShouldNotUpdate", "description": "NoDescription"}

    # Attempt to update a different company
    different_company_id = str(uuid4())
    response = test_client.put(
        f"{COMPANY_URL}/{different_company_id}",
        json=payload,
        headers=non_admin_headers,
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Not allowed across companies"

def test_update_company_non_admin_forbidden(test_client, non_admin_headers):
    """Test that non-admin users cannot update their own company."""
    # Get user's company id
    response = test_client.get(f"{COMPANY_URL}/me", headers=non_admin_headers)
    assert response.status_code == 200
    company_id = response.json()["id"]

    # Attempt to update own company as non-admin 
    response = test_client.put(
        f"{COMPANY_URL}/{company_id}",
        json={"name": "ShouldNotUpdate", "address": "NoAddress"},
        headers=non_admin_headers,
    )
    
    assert response.status_code == 403
    assert response.json()["detail"] == "Admin only"