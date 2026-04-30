"""
UserMaster — authentication table.
Maps to the users_master table defined in the DB schema.
All login credentials live here; role distinguishes teacher / student / parent / admin.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SAEnum
from sqlalchemy.orm import relationship
import enum

from app.db.session import Base


class UserRole(str, enum.Enum):
    teacher = "teacher"
    student = "student"
    parent = "parent"
    admin = "admin"


class UserMaster(Base):
    __tablename__ = "users_master"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(SAEnum(UserRole), nullable=False, default=UserRole.teacher)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationship: one user → one teacher profile
    teacher_profile = relationship("TeacherMaster", back_populates="user", uselist=False)
