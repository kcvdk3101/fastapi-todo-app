from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.database import get_db_context
from app.core.security import JWT_SECRET_KEY, JWT_ALGORITHM
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

CredentialsEx = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

def _decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        raise CredentialsEx

def _get_user_by_id(db: Session, user_id: UUID) -> User | None:
    return db.get(User, user_id)

def ensure_same_company(user: User, token_company_id: str | None):
    if token_company_id and str(user.company_id) != str(token_company_id):
        raise CredentialsEx

def ensure_active(user: User):
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Inactive user")

def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db_context),
) -> User:
    payload = _decode_token(token)
    sub = payload.get("sub")
    if not sub:
        raise CredentialsEx

    try:
        user_id = UUID(str(sub))
    except Exception:
        raise CredentialsEx

    user = _get_user_by_id(db, user_id)
    if not user:
        raise CredentialsEx

    ensure_active(user)
    ensure_same_company(user, payload.get("company_id"))

    return user
