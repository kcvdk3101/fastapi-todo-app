from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db_context
from app.core.security import get_password_hash
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserOut
from app.services.auth import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=UserOut)
def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user

@router.get("", response_model=list[UserOut])
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

@router.get("/{user_id}", response_model=UserOut)
def get_user(
    user_id: UUID,
    db: Session = Depends(get_db_context),
    current_user: User = Depends(get_current_user),
):
    user = db.get(User, user_id)
    if not user or user.company_id != current_user.company_id:
        raise HTTPException(status_code=404, detail="User not found")
    # user thường chỉ xem người cùng công ty (có thể siết chặt: chỉ xem bản thân)
    return user

@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
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
        company_id=current_user.company_id,  # luôn gán vào công ty của admin
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.patch("/{user_id}", response_model=UserOut)
def update_user(
    user_id: UUID,
    payload: UserUpdate,
    db: Session = Depends(get_db_context),
    current_user: User = Depends(get_current_user),
):
    user = db.get(User, user_id)
    if not user or user.company_id != current_user.company_id:
        raise HTTPException(status_code=404, detail="User not found")

    # quyền: user thường chỉ sửa chính mình + không được set is_admin/is_active cho người khác
    if not current_user.is_admin and user.id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    data = payload.model_dump(exclude_unset=True)

    # chặn leo quyền
    if not current_user.is_admin:
        data.pop("is_admin", None)
        data.pop("is_active", None)

    # đổi mật khẩu nếu có
    if "password" in data and data["password"]:
        user.hashed_password = get_password_hash(data.pop("password"))

    for k, v in data.items():
        setattr(user, k, v)

    db.commit()
    db.refresh(user)
    return user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
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
