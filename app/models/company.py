from __future__ import annotations
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from app.models.base import IdTimestampMixin, Base

class Company(IdTimestampMixin, Base):
    __tablename__ = "companies"

    name = Column(String, nullable=False)
    description = Column(String, nullable=True)

    users = relationship("User", back_populates="company", cascade="all, delete-orphan")