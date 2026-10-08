from datetime import datetime

from pydantic import EmailStr

from app.schemas.common import BaseSchema, RoleEnum


class UserBase(BaseSchema):
    name: str
    email: EmailStr
    role: RoleEnum
    organization_id: str
    is_active: bool = True


class UserCreate(BaseSchema):
    name: str
    email: EmailStr
    role: RoleEnum
    organization_id: str
    firebase_uid: str | None = None


class UserUpdate(BaseSchema):
    name: str | None = None
    role: RoleEnum | None = None
    is_active: bool | None = None


class UserRead(UserBase):
    id: str
    firebase_uid: str | None = None
    created_at: datetime


class SessionUser(BaseSchema):
    id: str
    name: str
    email: str
    role: RoleEnum
    organization_id: str
