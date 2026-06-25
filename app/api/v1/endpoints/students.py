from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_teacher
from app.models.teacher import TeacherMaster
from app.models.student import StudentMaster
from app.schemas.student import StudentListResponse, StudentOut

router = APIRouter(prefix="/students", tags=["students"])


@router.get("", response_model=StudentListResponse)
def list_students(
    teacher: TeacherMaster = Depends(get_current_teacher),
    db: Session = Depends(get_db),
):
    # Students linked to teacher via class_id (no direct teacher_id FK in sgs schema)
    students = (
        db.query(StudentMaster)
        .filter(StudentMaster.class_id == teacher.class_id)
        .order_by(StudentMaster.roll_no)
        .all()
    )
    return StudentListResponse(
        students=[StudentOut.model_validate(s) for s in students],
        total=len(students),
    )
