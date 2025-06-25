from sqlalchemy import Column, String, Integer, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ENUM
from datetime import datetime
import enum

from app.database import Base


class Role(enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"


role_enum = ENUM(Role, name="role")


class UserCourse(Base):
    __tablename__ = "user_course"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    course_id = Column(Integer, ForeignKey("courses.id"), primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="user_courses")
    course = relationship("Course", back_populates="user_courses")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    phone_number = Column(String(20))
    avatar = Column(String(200))
    role = Column(role_enum, default=Role.USER)
    auth0_id = Column(String(100), unique=True, index=True)

    user_courses = relationship("UserCourse", back_populates="user")

    courses = relationship("Course", secondary="user_course", viewonly=True)

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}', role='{self.role.name}')>"


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(Text)

    user_courses = relationship("UserCourse", back_populates="course")

    users = relationship("User", secondary="user_course", viewonly=True)

    def __repr__(self):
        return f"<Course(id={self.id}, title='{self.title}')>"
