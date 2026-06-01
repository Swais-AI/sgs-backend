from sqlalchemy import Column, BigInteger, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from app.db.session import Base


class LessonPlan(Base):
    __tablename__ = "sgs_lesson_plans"

    lesson_plan_id   = Column(BigInteger, primary_key=True)
    teacher_id       = Column(BigInteger, ForeignKey("sgs_teacher_master.teacher_id", ondelete="CASCADE"), nullable=False, index=True)
    title            = Column(String(300), nullable=False)
    subject          = Column(String(100), nullable=True)
    class_name       = Column(String(10),  nullable=True)
    section          = Column(String(5),   nullable=True)
    chapter_id       = Column(BigInteger,  nullable=True)
    chapter_text     = Column(String(300), nullable=True)
    duration_minutes = Column(Integer,     nullable=False, default=45)
    objectives       = Column(JSONB,       nullable=False, default=list)
    materials        = Column(JSONB,       nullable=False, default=list)
    core_concept     = Column(Text,        nullable=True)
    plan_sections    = Column(JSONB,       nullable=False, default=list)
    assessment_method= Column(Text,        nullable=True)
    homework         = Column(Text,        nullable=True)
    differentiation  = Column(JSONB,       nullable=True)
    prompt_used      = Column(Text,        nullable=True)
    modification_log = Column(JSONB,       nullable=False, default=list)
    created_at       = Column(DateTime,    nullable=True)
    updated_at       = Column(DateTime,    nullable=True)
    record_status    = Column(String(20),  nullable=True, default="Active")
    version_no       = Column(Integer,     nullable=True, default=1)
