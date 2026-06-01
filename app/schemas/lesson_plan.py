from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel


class LessonSection(BaseModel):
    title:          str
    duration:       int
    activity:       str
    teacher_action: str
    student_action: str


class GenerateRequest(BaseModel):
    chapter:          str
    topic:            Optional[str] = None
    duration_minutes: int = 45
    objectives:       List[str] = []
    special_notes:    Optional[str] = None


class LessonPlanOut(BaseModel):
    lesson_plan_id:   Optional[int] = None
    title:            str
    chapter_text:     Optional[str]
    subject:          Optional[str]
    class_name:       Optional[str]
    section:          Optional[str]
    duration_minutes: int
    objectives:       List[str]
    materials:        List[str]
    core_concept:     Optional[str]
    plan_sections:    List[Any]
    assessment_method:Optional[str]
    homework:         Optional[str]
    differentiation:  Optional[Any]
    created_at:       Optional[datetime] = None

    model_config = {"from_attributes": True}


class LessonPlanListResponse(BaseModel):
    plans: List[LessonPlanOut]
    total: int


class SaveRequest(BaseModel):
    plan: LessonPlanOut
