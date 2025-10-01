import pytest
from uuid import uuid4

from jose import JWTError

from app.services import auth as auth_module
from app.services.auth import (
    _decode_token,
    ensure_active,
    ensure_same_company,
    get_current_user,
)


class StubUser:
    def __init__(self, user_id, is_active=True, company_id=None):
        self.id = user_id
        self.is_active = is_active
        self.company_id = company_id


class StubDB:
    def __init__(self, user=None):
        self._user = user

    def get(self, model, user_id):
        # Return the configured stub user if ids match; else None
        if self._user and str(self._user.id) == str(user_id):
            return self._user
        return None


# Helpers / fixtures
@pytest.fixture
def active_user():
    return StubUser(user_id=uuid4(), is_active=True, company_id=uuid4())


@pytest.fixture
def inactive_user(active_user):
    return StubUser(user_id=active_user.id, is_active=False, company_id=active_user.company_id)


@pytest.fixture
def db_with_user(active_user):
    return StubDB(user=active_user)


@pytest.fixture
def empty_db():
    return StubDB(user=None)


def set_jwt_decode(monkeypatch, *, payload=None, error: Exception | None = None):
    if error is not None:
        def fake_decode(token, key, algorithms):
            raise error
    else:
        def fake_decode(token, key, algorithms):
            return payload
    monkeypatch.setattr(auth_module.jwt, "decode", fake_decode)


def test_decode_token_valid(monkeypatch):
    payload = {"sub": str(uuid4()), "company_id": str(uuid4())}
    set_jwt_decode(monkeypatch, payload=payload)
    assert _decode_token("token123") == payload


def test_decode_token_invalid_raises_credentials(monkeypatch):
    set_jwt_decode(monkeypatch, error=JWTError("bad token"))
    with pytest.raises(Exception) as excinfo:
        _decode_token("token123")
    # HTTPException with 401 is raised (CredentialsEx)
    assert getattr(excinfo.value, "status_code", None) == 401


def test_ensure_active_allows_active_user(active_user):
    # Should not raise
    ensure_active(active_user)


def test_ensure_active_raises_for_inactive_user(inactive_user):
    with pytest.raises(Exception) as excinfo:
        ensure_active(inactive_user)
    assert getattr(excinfo.value, "status_code", None) == 403
    assert getattr(excinfo.value, "detail", None) == "Inactive user"


def test_ensure_same_company_allows_when_matches(active_user):
    # Should not raise
    ensure_same_company(active_user, str(active_user.company_id))


def test_ensure_same_company_raises_when_mismatch(active_user):
    with pytest.raises(Exception) as excinfo:
        ensure_same_company(active_user, str(uuid4()))
    assert getattr(excinfo.value, "status_code", None) == 401


def test_get_current_user_success(monkeypatch, active_user):
    payload = {"sub": str(active_user.id), "company_id": str(active_user.company_id)}
    set_jwt_decode(monkeypatch, payload=payload)
    db = StubDB(user=active_user)
    current_user = get_current_user(token="token123", db=db)
    assert current_user is active_user


def test_get_current_user_raises_for_missing_sub(monkeypatch, empty_db):
    set_jwt_decode(monkeypatch, payload={"company_id": str(uuid4())})
    with pytest.raises(Exception) as excinfo:
        get_current_user(token="token123", db=empty_db)
    assert getattr(excinfo.value, "status_code", None) == 401


def test_get_current_user_raises_for_nonexistent_user(monkeypatch, empty_db):
    payload = {"sub": str(uuid4()), "company_id": str(uuid4())}
    set_jwt_decode(monkeypatch, payload=payload)
    with pytest.raises(Exception) as excinfo:
        get_current_user(token="token123", db=empty_db)
    assert getattr(excinfo.value, "status_code", None) == 401


def test_get_current_user_raises_for_inactive_user(monkeypatch, inactive_user):
    payload = {"sub": str(inactive_user.id), "company_id": str(inactive_user.company_id)}
    set_jwt_decode(monkeypatch, payload=payload)
    db = StubDB(user=inactive_user)
    with pytest.raises(Exception) as excinfo:
        get_current_user(token="token123", db=db)
    assert getattr(excinfo.value, "status_code", None) == 403
    assert getattr(excinfo.value, "detail", None) == "Inactive user"


def test_get_current_user_raises_for_company_mismatch(monkeypatch, active_user):
    payload = {"sub": str(active_user.id), "company_id": str(uuid4())}
    set_jwt_decode(monkeypatch, payload=payload)
    db = StubDB(user=active_user)
    with pytest.raises(Exception) as excinfo:
        get_current_user(token="token123", db=db)
    assert getattr(excinfo.value, "status_code", None) == 401


