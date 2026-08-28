from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class LessonPlanGenerateRequest(BaseModel):
    chapterId: int
    # The teacher may retitle the chapter on the form; `topic` is the new name
    # for it. `chapterName` is the name the older frontend sends — accepted so
    # a stale build keeps working.
    topic: Optional[str] = None
    chapterName: Optional[str] = None
    noOfPeriods: int = 1
    dateOfCommencement: Optional[date] = None
    expectedCompletion: Optional[date] = None
    # Header fields default to the teacher's own record; sent only when the
    # teacher overrides them on the form.
    classSection: Optional[str] = None
    subject: Optional[str] = None
    designation: Optional[str] = None
    schoolName: Optional[str] = None

    @property
    def chapter(self) -> str:
        return (self.topic or self.chapterName or "").strip()


class LessonPlanSaveRequest(BaseModel):
    plan: dict


class LessonPlanCompletionRequest(BaseModel):
    """Recorded after the lesson is actually taught, not at generation time."""
    actualCompletion: date


class LessonPlanOut(BaseModel):
    lesson_plan_id: int
    title: str
    chapter_text: Optional[str]
    duration_minutes: Optional[int]
    created_at: Optional[datetime]
    # Full structured plan (parsed from the stored plan_data JSON) so the
    # "View" action can render the whole plan without a second request.
    plan: Optional[dict] = None

    class Config:
        from_attributes = True


class LessonPlanListResponse(BaseModel):
    plans: list[LessonPlanOut]
