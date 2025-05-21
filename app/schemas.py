from pydantic import BaseModel, EmailStr, Field, ValidationError
from typing import Optional
from enum import Enum
from fastapi import Form
import re

class Role(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    phone_number: Optional[str] = Field(None, pattern=r"^\+?[1-9]\d{1,14}$")
    avatar: Optional[str] = None

class UserCreate(UserBase):
    role: Role = Role.USER

class UserUpdateForm:
    def __init__(
        self,
        username: Optional[str] = Form(None),
        email: Optional[str] = Form(None),
        phone_number: Optional[str] = Form(None),
        avatar: Optional[str] = Form(None),
    ):
        if username is not None and not (3 <= len(username) <= 50):
            raise ValueError("Username must be between 3 and 50 characters")
        if email is not None:
            try:
                EmailStr._validate(email)
            except ValidationError:
                raise ValueError("Invalid email")
        if phone_number is not None:
            if not re.match(r"^\+?[1-9]\d{1,14}$", phone_number):
                raise ValueError("Invalid phone number format")

        self.username = username
        self.email = email
        self.phone_number = phone_number
        self.avatar = avatar

    def dict(self, exclude_unset=True):
        return {k: v for k, v in vars(self).items() if v is not None or not exclude_unset}

class UserInDB(UserBase):
    id: str
    role: Role
    auth0_id: str

    class Config:
        from_attributes = True

class UserResponse(UserInDB):
    class Config:
        fields = {"auth0_id": {"exclude": True}}

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

class CourseRead(CourseCreate):
    id: int

    class Config:
        from_attributes = True