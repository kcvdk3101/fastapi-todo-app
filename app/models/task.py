from __future__ import annotations
from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import IdTimestampMixin, Base

class Task(IdTimestampMixin, Base):
    __tablename__ = "tasks"

    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    is_completed = Column(Boolean, default=False)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="RESTRICT"), nullable=False)

    owner = relationship("User", back_populates="tasks")