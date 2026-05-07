from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.models.student import Gender


class StudentOut(BaseModel):
    student_id:   int
    name:         str
    roll_number:  str
    gender:       Optional[Gender]
    parent_name:  Optional[str]
    parent_phone: Optional[str]
    class_name:   Optional[str]
    section:      Optional[str]

    model_config = {"from_attributes": True}


class StudentListResponse(BaseModel):
    students: list[StudentOut]
    total:    int
