from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.url import auth
from app.core.database import get_db_context
from app.core.security import verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from app.models.user import User

router = APIRouter(prefix=auth["prefix"], tags=auth["tags"])

# Login by username (or email)
@router.post(auth["urls"]["login"])
def login(
    form: OAuth2PasswordRequestForm = Depends(),  # fields: username, password
    db: Session = Depends(get_db_context),
):
    user = db.query(User).filter(User.username == form.username).first()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect credentials")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(
        subject=str(user.id),
        expires_delta=access_token_expires,
        extra_claims={
            "company_id": str(user.company_id),
            "is_admin": user.is_admin,
        },
    )
    return {"access_token": token, "token_type": "bearer"}
