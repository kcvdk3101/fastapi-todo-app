from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.url import user
from app.core.database import get_db_context
from app.core.security import get_password_hash
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserOut
from app.services.auth import get_current_user

router = APIRouter(prefix=user["prefix"], tags=user["tags"])

# Get user profile
@router.get(user["urls"]["get_me"], response_model=UserOut)
def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user

# Get user list
@router.get(user["urls"]["list_users"], response_model=list[UserOut])
def list_users_in_company(
    db: Session = Depends(get_db_context),
    current_user: User = Depends(get_current_user),
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin only")
    return (
        db.query(User)
        .filter(User.company_id == current_user.company_id)
        .all()
    )

# Get user profile by id
@router.get(user["urls"]["get_user_by_id"], response_model=UserOut)
def get_user(
    user_id: UUID,
    db: Session = Depends(get_db_context),
    current_user: User = Depends(get_current_user),
):
    user = db.get(User, user_id)
    if not user or user.company_id != current_user.company_id:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Create user (admin only)
@router.post(user["urls"]["create_user"], response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user_in_company(
    payload: UserCreate,
    db: Session = Depends(get_db_context),
    current_user: User = Depends(get_current_user),
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin only")

    hashed = get_password_hash(payload.password)
    user = User(
        email=payload.email,
        username=payload.username,
        first_name=payload.first_name,
        last_name=payload.last_name,
        hashed_password=hashed,
        is_active=payload.is_active,
        is_admin=payload.is_admin,
        company_id=current_user.company_id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# Update user profile by id
@router.put(user["urls"]["update_user"], response_model=UserOut)
def update_user(
    user_id: UUID,
    payload: UserUpdate,
    db: Session = Depends(get_db_context),
    current_user: User = Depends(get_current_user),
):
    user = db.get(User, user_id)
    if not user or user.company_id != current_user.company_id:
        raise HTTPException(status_code=404, detail="User not found")

    # User only update basic information, except is_admin/is_active
    if not current_user.is_admin and user.id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    data = payload.model_dump(exclude_unset=True)

    # Prevent unauthorized access
    if not current_user.is_admin:
        data.pop("is_admin", None)
        data.pop("is_active", None)

    # Change pasword
    if "password" in data and data["password"]:
        user.hashed_password = get_password_hash(data.pop("password"))

    for k, v in data.items():
        setattr(user, k, v)

    db.commit()
    db.refresh(user)
    return user

# Delete user (admin only)
@router.delete(user["urls"]["delete_user"], status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: UUID,
    db: Session = Depends(get_db_context),
    current_user: User = Depends(get_current_user),
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin only")

    user = db.get(User, user_id)
    if not user or user.company_id != current_user.company_id:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
