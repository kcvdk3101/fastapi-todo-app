from uuid import UUID
from pydantic import BaseModel, Field

class Task(BaseModel):
  title: str = Field(min_length=1)
  content: str = Field(min_length=1)
  is_completed: bool = Field(default=False)

class TaskCreate(Task):
  pass

class TaskUpdate(BaseModel):
  title: str = Field(min_length=1)
  content: str = Field(min_length=1)

class TaskOut(Task):
    user_id: UUID
    company_id: UUID

    class Config:
        from_attributes = True