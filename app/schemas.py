from dataclasses import dataclass
from pydantic import BaseModel, EmailStr, Field, ConfigDict, model_serializer
from typing import Optional
from fastapi import Form, UploadFile, File
from app.models import Role

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    phone_number: Optional[str] = Field(None, pattern=r"^\+?[1-9]\d{1,14}$")
    avatar: Optional[str] = None

class UserCreate(UserBase):
    role: Role = Role.USER

@dataclass
class UserUpdateForm:
    username: Optional[str]
    email: Optional[str]
    phone_number: Optional[str]
    avatar: Optional[UploadFile]

    def dict(self, exclude_unset: bool = True):
        return {
            k: v
            for k, v in {
                "username": self.username,
                "email": self.email,
                "phone_number": self.phone_number,
            }.items()
            if v is not None or not exclude_unset
        }

    @classmethod
    def as_form(cls):
        def _as_form(
            username: Optional[str] = Form(None),
            email: Optional[str] = Form(None),
            phone_number: Optional[str] = Form(None),
            avatar: Optional[UploadFile] = File(None),
        ) -> "UserUpdateForm":
            return cls(username, email, phone_number, avatar)
        return _as_form

class UserInDB(UserBase):
    id: str
    role: Role
    auth0_id: str

    class Config:
        from_attributes = True

class UserResponse(UserInDB):
    model_config = ConfigDict(from_attributes=True)

    @model_serializer
    def serialize(self):
        data = self.model_dump()
        data.pop('auth0_id', None)
        return data

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    sub: Optional[str] = None
    email: Optional[str] = None
    roles: list[str] = []

class CourseCreate(BaseModel):
    title: str
    description: str | None = None

class CourseUpdate(BaseModel):
    title: str
    description: str | None = None

class CourseRead(CourseCreate):
    id: int

    class Config:
        from_attributes = True