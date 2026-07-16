from pydantic import BaseModel


class SubjectOut(BaseModel):
    subject_id: int
    subject_name: str | None = None
    subject_code: str | None = None


class SubjectListResponse(BaseModel):
    subjects: list[SubjectOut]
    total: int
