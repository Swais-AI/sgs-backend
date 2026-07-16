from datetime import date
from pydantic import BaseModel


class AssignmentOut(BaseModel):
    assignment_id: int
    title: str | None = None
    subject: str | None = None
    chapter_id: int | None = None
    due_date: date | None = None
    submitted_count: int = 0
    total_students: int = 0


class AssignmentListResponse(BaseModel):
    assignments: list[AssignmentOut]
    total: int


class AssignmentCreate(BaseModel):
    title: str
    text: str | None = None
    subject_id: int | None = None
    chapter_id: int | None = None
    due_date: date | None = None
