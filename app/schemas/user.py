from uuid import UUID
from pydantic import BaseModel, Field

class User(BaseModel):
    email: str = Field(min_length=1)
    username: str = Field(min_length=3, max_length=50)
    first_name: str | None = Field(default=None, max_length=50)
    last_name: str | None = Field(default=None, max_length=50)
    is_active: bool = True
    is_admin: bool = False

class UserCreate(User):
    password: str = Field(min_length=6, max_length=128)

class UserUpdate(BaseModel):
    email: str | None = None
    username: str | None = Field(default=None, min_length=3, max_length=50)
    first_name: str | None = Field(default=None, max_length=50)
    last_name: str | None = Field(default=None, max_length=50)
    is_active: bool | None = None
    is_admin: bool | None = None 
    password: str | None = Field(default=None, min_length=6, max_length=128)

class UserOut(User):
    company_id: UUID

    class Config:
        from_attributes = True
