from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_teacher
from app.models.teacher import TeacherMaster
from app.schemas.subject import SubjectListResponse
from app.services import subject_service

router = APIRouter(prefix="/subjects", tags=["subjects"])


@router.get("", response_model=SubjectListResponse)
def list_subjects(
    teacher: TeacherMaster = Depends(get_current_teacher),
    db: Session = Depends(get_db),
):
    """List subjects for the authenticated teacher's class."""
    subjects = subject_service.get_subjects(db, teacher)
    return SubjectListResponse(subjects=subjects, total=len(subjects))
