import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role_id: int | None = None

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v

    @field_validator("full_name")
    @classmethod
    def full_name_length(cls, v: str) -> str:
        if len(v.strip()) < 2:
            raise ValueError("full_name must be at least 2 characters")
        if len(v) > 150:
            raise ValueError("full_name must be at most 150 characters")
        return v.strip()


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    full_name: str | None = None
    role_id: int | None = None
    is_active: bool | None = None


class RoleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    full_name: str
    role_id: int | None = None
    role: RoleResponse | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
