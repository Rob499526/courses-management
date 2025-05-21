from sqlalchemy import Column, String, Enum, Integer, Text
from sqlalchemy.dialects.postgresql import ENUM
from app.database import Base
import enum

class Role(enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"

role_enum = ENUM(Role, name="role", create_type=True)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    phone_number = Column(String(20))
    avatar = Column(String(200))
    role = Column(role_enum, default=Role.USER)
    auth0_id = Column(String(100), unique=True)

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(Text)