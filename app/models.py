from sqlalchemy import Column, String, Integer, Text, ForeignKey, Table
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import relationship

from app.database import Base
import enum

class Role(enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"

role_enum = ENUM(Role, name="role")

user_course_table = Table(
    "user_course",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("course_id", ForeignKey("courses.id"), primary_key=True),
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    phone_number = Column(String(20))
    avatar = Column(String(200))
    role = Column(role_enum, default=Role.USER)
    auth0_id = Column(String(100), unique=True, index=True)
    courses = relationship("Course", secondary="user_course", back_populates="users")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}', role='{self.role.name}')>"

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(Text)
    users = relationship("User", secondary="user_course", back_populates="courses")

    def __repr__(self):
        return f"<Course(id={self.id}, title='{self.title}')>"

