from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db_context
from app.models.company import Company
from app.models.user import User
from app.schemas.company import CompanyCreate, CompanyUpdate, CompanyOut
from app.services.auth import get_current_user

router = APIRouter(prefix="/companies", tags=["Companies"])

@router.get("/me", response_model=CompanyOut)
def get_my_company(
    db: Session = Depends(get_db_context),
    current_user: User = Depends(get_current_user),
):
    comp = db.get(Company, current_user.company_id)
    if not comp:
        raise HTTPException(status_code=404, detail="Company not found")
    return comp

@router.get("/{company_id}", response_model=CompanyOut)
def get_company(
    company_id: UUID,
    db: Session = Depends(get_db_context),
    current_user: User = Depends(get_current_user),
):
    if company_id != current_user.company_id:
        raise HTTPException(status_code=403, detail="Not allowed across companies")
    comp = db.get(Company, company_id)
    if not comp:
        raise HTTPException(status_code=404, detail="Company not found")
    return comp

@router.patch("/{company_id}", response_model=CompanyOut)
def update_company(
    company_id: UUID,
    payload: CompanyUpdate,
    db: Session = Depends(get_db_context),
    current_user: User = Depends(get_current_user),
):
    if company_id != current_user.company_id:
        raise HTTPException(status_code=403, detail="Not allowed across companies")
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin only")

    comp = db.get(Company, company_id)
    if not comp:
        raise HTTPException(status_code=404, detail="Company not found")

    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(comp, k, v)
    db.commit()
    db.refresh(comp)
    return comp

# Tuỳ chính sách, tạo Company thường do super-admin.
# Nếu vẫn muốn cho phép admin tạo company mới, giữ endpoint sau và tự gắn user vào công ty mới qua flow riêng.
@router.post("", response_model=CompanyOut, status_code=status.HTTP_201_CREATED)
def create_company(
    payload: CompanyCreate,
    db: Session = Depends(get_db_context),
    current_user: User = Depends(get_current_user),
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin only")
    comp = Company(**payload.model_dump())
    db.add(comp)
    db.commit()
    db.refresh(comp)
    return comp
