import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class PersonBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    phone: str = Field(..., min_length=7, max_length=50)
    email: Optional[EmailStr] = None
    avatar_url: Optional[str] = None
    is_active: bool = True


class PersonCreate(PersonBase):
    pass


class PersonUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    avatar_url: Optional[str] = None
    is_active: Optional[bool] = None


class PersonResponse(PersonBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
