from datetime import datetime, timezone, date
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Date, Enum as SAEnum, Text
from sqlalchemy.orm import relationship
import enum

from app.db.session import Base


class AssessmentType(str, enum.Enum):
    quiz        = "quiz"
    test        = "test"
    exam        = "exam"
    assignment  = "assignment"


class Assessment(Base):
    __tablename__ = "assessments"

    assessment_id   = Column(Integer, primary_key=True, autoincrement=True)
    teacher_id      = Column(Integer, ForeignKey("teacher_master.teacher_id", ondelete="CASCADE"), nullable=False, index=True)

    title           = Column(String(300), nullable=False)
    chapter         = Column(String(255), nullable=True)
    assessment_type = Column(SAEnum(AssessmentType), nullable=False, default=AssessmentType.test)
    max_marks       = Column(Float, nullable=False, default=100.0)
    assessment_date = Column(Date, nullable=True)
    description     = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    teacher = relationship("TeacherMaster", back_populates="assessments")
    results = relationship("AssessmentResult", back_populates="assessment", cascade="all, delete-orphan")


class AssessmentResult(Base):
    __tablename__ = "assessment_results"

    result_id      = Column(Integer, primary_key=True, autoincrement=True)
    assessment_id  = Column(Integer, ForeignKey("assessments.assessment_id", ondelete="CASCADE"), nullable=False, index=True)
    student_id     = Column(Integer, ForeignKey("student_master.student_id", ondelete="CASCADE"), nullable=False, index=True)

    marks_obtained = Column(Float, nullable=True)   # null = absent
    remarks        = Column(String(300), nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    assessment = relationship("Assessment", back_populates="results")
    student    = relationship("StudentMaster", back_populates="results")
