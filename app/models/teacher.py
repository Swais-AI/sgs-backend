"""
TeacherMaster — teacher profile data.
Linked to users_master via user_id FK (added by migration).
Stores school, subject, class, section and other profile info.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship

from app.db.session import Base


class TeacherMaster(Base):
    __tablename__ = "teacher_master"

    teacher_id = Column(Integer, primary_key=True, autoincrement=True)

    # Link to users_master — added via our migration
    user_id = Column(
        Integer,
        ForeignKey("users_master.user_id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    # Teacher profile fields (from DB schema)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)          # stored as string, not INT
    avatar_initials = Column(String(5), nullable=True)  # e.g. "PS"
    subject = Column(String(100), nullable=True)
    class_assigned = Column(String(10), nullable=True)  # e.g. "8"
    section = Column(String(10), nullable=True)         # e.g. "A"
    school_name = Column(String(255), nullable=True)
    employee_code = Column(String(50), nullable=True)
    address = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    user        = relationship("UserMaster", back_populates="teacher_profile")
    notes       = relationship("TeacherNote",      back_populates="teacher", cascade="all, delete-orphan")
    students    = relationship("StudentMaster",     back_populates="teacher", cascade="all, delete-orphan")
    assessments = relationship("Assessment",        back_populates="teacher", cascade="all, delete-orphan")
