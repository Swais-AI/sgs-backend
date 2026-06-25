"""
TeacherNote — maps to sgs_teacher_notes table.
Rich note data (title, content, chapter, content_type, tags) is stored
as a JSON string in the `notes` column since the sgs table has no separate fields.
"""

import enum
from sqlalchemy import Column, BigInteger, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.db.session import Base


class ContentType(str, enum.Enum):
    typed       = "typed"
    voice       = "voice"
    handwritten = "handwritten"


class TeacherNote(Base):
    __tablename__ = "sgs_teacher_notes"

    notes_id   = Column(BigInteger, primary_key=True)
    teacher_id = Column(
        BigInteger,
        ForeignKey("sgs_teacher_master.teacher_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    class_id   = Column(BigInteger, nullable=True)
    section_1  = Column(String(50), nullable=True)
    notes      = Column(String, nullable=True)   # stores JSON: {title, content, chapter, ...}
    created_at = Column(DateTime, nullable=True)

    teacher = relationship("TeacherMaster", back_populates="notes")
