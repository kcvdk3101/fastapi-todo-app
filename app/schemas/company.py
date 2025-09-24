from uuid import UUID
from pydantic import BaseModel, Field

class Company(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=1024)

class CompanyCreate(Company):
    pass

class CompanyUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    description: str | None = Field(default=None, max_length=1024)

class CompanyOut(Company):
    id: UUID

    class Config:
        from_attributes = True
