from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, field_validator

from app.models.note import ContentType


class NoteCreate(BaseModel):
    title: str
    content: Optional[str] = None
    chapter: str
    content_type: ContentType = ContentType.typed
    canvas_image_url: Optional[str] = None
    tags: List[str] = []

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip()

    @field_validator("chapter")
    @classmethod
    def chapter_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Chapter cannot be empty")
        return v.strip()


class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    chapter: Optional[str] = None
    content_type: Optional[ContentType] = None
    canvas_image_url: Optional[str] = None
    tags: Optional[List[str]] = None


class NoteOut(BaseModel):
    id: str           # returned as "N{note_id}" to match frontend format
    title: str
    content: Optional[str]
    chapter: str
    contentType: ContentType
    canvasImageUrl: Optional[str]
    tags: List[str]
    createdAt: datetime
    updatedAt: datetime

    model_config = {"from_attributes": True}


class NoteListResponse(BaseModel):
    notes: List[NoteOut]
    total: int
