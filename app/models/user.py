from __future__ import annotations
from sqlalchemy import Boolean, Column, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import IdTimestampMixin, Base

class User(IdTimestampMixin, Base):
    __tablename__ = "users"

    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)

    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)

    company = relationship("Company", back_populates="users")
    tasks = relationship("Task", back_populates="owner")
