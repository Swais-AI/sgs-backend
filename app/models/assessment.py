from datetime import date
from sqlalchemy import Column, BigInteger, Integer, String, Float, ForeignKey, DateTime, Date, Enum as SAEnum, Boolean, Numeric
from sqlalchemy.orm import relationship
import enum

from app.db.session import Base


class AssessmentType(str, enum.Enum):
    quiz       = "quiz"
    test       = "test"
    exam       = "exam"
    assignment = "assignment"


class Assessment(Base):
    __tablename__ = "sgs_assessments"

    assessment_id   = Column(BigInteger, primary_key=True)
    teacher_id      = Column(BigInteger, ForeignKey("sgs_teacher_master.teacher_id", ondelete="CASCADE"), nullable=False, index=True)
    title           = Column(String(300), nullable=False)
    assessment_type = Column(SAEnum(AssessmentType, name="assessment_type", create_type=False), nullable=False, default=AssessmentType.test)
    chapter_id      = Column(BigInteger, nullable=True)
    chapter         = Column(String(300), nullable=True)
    assessment_date = Column(Date, nullable=True)
    max_marks       = Column(Numeric(6, 2), nullable=False, default=100)
    class_name      = Column(String(10), nullable=False, default="")
    section         = Column(String(5), nullable=False, default="")
    total_students  = Column(Integer, nullable=False, default=0)
    submitted       = Column(Integer, nullable=False, default=0)
    class_average   = Column(Numeric(5, 2), nullable=True)
    created_at      = Column(DateTime, nullable=True)
    updated_at      = Column(DateTime, nullable=True)
    record_status   = Column(String(20), nullable=True)
    version_no      = Column(Integer, nullable=True)

    teacher = relationship("TeacherMaster", back_populates="assessments")
    results = relationship("AssessmentResult", back_populates="assessment", cascade="all, delete-orphan")


class AssessmentResult(Base):
    __tablename__ = "sgs_assessment_results"

    result_id      = Column(BigInteger, primary_key=True)
    assessment_id  = Column(BigInteger, ForeignKey("sgs_assessments.assessment_id", ondelete="CASCADE"), nullable=False, index=True)
    student_id     = Column(BigInteger, ForeignKey("sgs_student_master.student_id", ondelete="CASCADE"), nullable=False, index=True)
    roll_number    = Column(String(20), nullable=False, default="")
    student_name   = Column(String(150), nullable=False, default="")
    marks_obtained = Column(Numeric(6, 2), nullable=True)
    percentage     = Column(Numeric(5, 2), nullable=True)
    is_absent      = Column(Boolean, nullable=False, default=False)
    created_at     = Column(DateTime, nullable=True)
    updated_at     = Column(DateTime, nullable=True)
    record_status  = Column(String(20), nullable=True)
    version_no     = Column(Integer, nullable=True)

    assessment = relationship("Assessment", back_populates="results")
