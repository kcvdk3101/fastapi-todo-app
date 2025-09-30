from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field

class Task(BaseModel):
  title: str = Field(min_length=1)
  content: str = Field(min_length=1)
  is_completed: bool = Field(default=False)
  created_at: datetime | None = None
  updated_at: datetime | None = None

class TaskCreate(Task):
  pass

class TaskUpdate(BaseModel):
  title: str = Field(min_length=1)
  content: str = Field(min_length=1)
  is_completed: bool

class TaskOut(Task):
    id: UUID
    user_id: UUID
    company_id: UUID

    class Config:
        from_attributes = True