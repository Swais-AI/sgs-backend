from typing import Optional
from pydantic import BaseModel, Field


class StudentOut(BaseModel):
    student_id:    int
    full_name:     Optional[str] = None
    roll_no:       Optional[str] = None
    guardian_name: Optional[str] = None
    guardian_phone: Optional[str] = None
    section:       Optional[str] = None

    model_config = {"from_attributes": True}


class StudentListResponse(BaseModel):
    students: list[StudentOut]
    total:    int
