"""
TeacherNote — teacher_notes table (new table created by our migration).
Stores typed, voice-transcribed, and handwritten notes created by faculty.
canvasImageUrl stores base64 PNG for handwritten notes (TODO: move to S3).

This content is the source material for:
  - Student/parent delivery (voice TTS via AWS Polly — future)
  - Chapter-wise curriculum notes
"""

import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Enum as SAEnum, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB

from app.db.session import Base


class ContentType(str, enum.Enum):
    typed = "typed"
    voice = "voice"
    handwritten = "handwritten"


class TeacherNote(Base):
    __tablename__ = "sgs_faculty_notes"

    note_id = Column(Integer, primary_key=True, autoincrement=True)

    teacher_id = Column(
        Integer,
        ForeignKey("sgs_teacher_master.teacher_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=True)               # Text content (typed or voice transcript)
    chapter = Column(String(255), nullable=False)       # e.g. "Chapter 1 - The Indian Constitution"
    content_type = Column(SAEnum(ContentType), nullable=False, default=ContentType.typed)
    canvas_image_url = Column(Text, nullable=True)      # base64 PNG; TODO: replace with S3 URL
    tags = Column(JSONB, nullable=True, default=list)   # ["constitution", "preamble"]

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationship
    teacher = relationship("TeacherMaster", back_populates="notes")
