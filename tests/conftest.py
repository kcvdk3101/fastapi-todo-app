from fastapi.testclient import TestClient
from app.main import app
import pytest

client = TestClient(app)

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

# Fixture for creating a test company
@pytest.fixture
def test_company(test_db):
    from app.models.company import Company
    company = Company(name="TestCompany", description="TestDescription")
    test_db.add(company)
    test_db.commit()
    test_db.refresh(company)
    yield company
    test_db.delete(company)
    test_db.commit()