from typing import Optional
from pydantic import BaseModel


class StudentOut(BaseModel):
    student_id:     int
    full_name:      Optional[str]
    roll_no:        Optional[str]
    class_id:       Optional[int]
    section:        Optional[str]
    guardian_name:  Optional[str]
    guardian_phone: Optional[str]
    guardian_email: Optional[str]

    model_config = {"from_attributes": True}


class StudentListResponse(BaseModel):
    students: list[StudentOut]
    total:    int
