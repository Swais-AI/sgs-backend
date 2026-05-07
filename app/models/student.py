from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum as SAEnum
from sqlalchemy.orm import relationship
import enum

from app.db.session import Base


class Gender(str, enum.Enum):
    male = "male"
    female = "female"
    other = "other"


class StudentMaster(Base):
    __tablename__ = "student_master"

    student_id   = Column(Integer, primary_key=True, autoincrement=True)
    teacher_id   = Column(Integer, ForeignKey("teacher_master.teacher_id", ondelete="CASCADE"), nullable=False, index=True)

    name         = Column(String(150), nullable=False)
    roll_number  = Column(String(20),  nullable=False)
    gender       = Column(SAEnum(Gender), nullable=True)
    parent_name  = Column(String(150), nullable=True)
    parent_phone = Column(String(20),  nullable=True)
    class_name   = Column(String(10),  nullable=True)   # "8"
    section      = Column(String(10),  nullable=True)   # "A"

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    teacher = relationship("TeacherMaster", back_populates="students")
    results = relationship("AssessmentResult", back_populates="student", cascade="all, delete-orphan")
