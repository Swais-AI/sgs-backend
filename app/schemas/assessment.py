from datetime import date
from typing import Optional, List
from pydantic import BaseModel
from app.models.assessment import AssessmentType


class ResultOut(BaseModel):
    result_id:      int
    student_id:     int
    student_name:   str
    roll_number:    str
    marks_obtained: Optional[float]
    max_marks:      float
    percentage:     Optional[float]

    model_config = {"from_attributes": True}


class AssessmentOut(BaseModel):
    assessment_id:   int
    title:           str
    subject:         Optional[str]
    chapter:         Optional[str]
    assessment_type: AssessmentType
    max_marks:       float
    assessment_date: Optional[date]
    total_students:  int
    submitted:       int
    class_average:   Optional[float]

    model_config = {"from_attributes": True}


class AssessmentDetailOut(AssessmentOut):
    results: List[ResultOut]


class AssessmentListResponse(BaseModel):
    assessments: List[AssessmentOut]
    total:       int
