from sqlalchemy import Column, BigInteger, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.db.session import Base


class TeacherMaster(Base):
    __tablename__ = "sgs_teacher_master"

    teacher_id   = Column(BigInteger, primary_key=True)
    email_id     = Column(String(255), nullable=True, index=True)
    full_name    = Column(String(200), nullable=True)
    subject_name = Column(String(100), nullable=True)
    class_id     = Column(BigInteger, nullable=True)
    section_1    = Column(String(10), nullable=True)
    section_2    = Column(String(10), nullable=True)
    phone        = Column(String(20), nullable=True)
    role         = Column(String(50), nullable=True)
    is_active    = Column(Boolean, nullable=True)
    created_at   = Column(DateTime, nullable=True)

    notes       = relationship("TeacherNote", back_populates="teacher", cascade="all, delete-orphan")
    assessments = relationship("Assessment",  back_populates="teacher", cascade="all, delete-orphan")
