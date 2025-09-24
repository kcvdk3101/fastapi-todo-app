from __future__ import annotations

import os
from sqlalchemy import select
from dotenv import load_dotenv

from app.core.database import LocalSession
from app.core.security import get_password_hash
from app.models.company import Company
from app.models.user import User

def seed_admin(
    *,
    company_name: str,
    company_description: str,
    admin_email: str,
    admin_username: str,
    admin_password: str,
    admin_first_name: str,
    admin_last_name: str,
) -> None:
    db = LocalSession()
    try:
        company = db.execute(
            select(Company).where(Company.name == company_name)
        ).scalar_one_or_none()

        if not company:
            company = Company(
                name=company_name,
                description=company_description,
            )
            db.add(company)
            db.flush()

        user = db.execute(
            select(User).where(User.email == admin_email)
        ).scalar_one_or_none()

        if not user:
            user = User(
                email=admin_email,
                username=admin_username,
                first_name=admin_first_name,
                last_name=admin_last_name,
                hashed_password=get_password_hash(admin_password),
                is_active=True,
                is_admin=True,
                company_id=company.id,
            )
            db.add(user)
        else:
            user.company_id = company.id
            user.is_active = True
            user.is_admin = True

            user.username = admin_username or user.username
            if admin_first_name: user.first_name = admin_first_name
            if admin_last_name is not None: user.last_name = admin_last_name

        db.commit()

        db.refresh(company)
        db.refresh(user)

        print("✅ Seed completed")
        print(f"   Company: {company.name} (id={company.id})")
        print(f"   Admin  : {user.email} / username={user.username} (id={user.id})")

    finally:
        db.close()


if __name__ == "__main__":
    load_dotenv()

    company_name = os.getenv("SEED_COMPANY_NAME")
    company_desc = os.getenv("SEED_COMPANY_DESC")

    admin_email = os.getenv("SEED_ADMIN_EMAIL")
    admin_username = os.getenv("SEED_ADMIN_USERNAME")
    admin_password = os.getenv("SEED_ADMIN_PASSWORD")
    admin_first = os.getenv("SEED_ADMIN_FIRST")
    admin_last = os.getenv("SEED_ADMIN_LAST")

    seed_admin(
        company_name=company_name,
        company_description=company_desc,
        admin_email=admin_email,
        admin_username=admin_username,
        admin_password=admin_password,
        admin_first_name=admin_first,
        admin_last_name=admin_last,
    )
