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
    # Students are linked to a class, not directly to a teacher — filter by class_id + section
    query = db.query(StudentMaster).filter(StudentMaster.is_active == True)
    if teacher.class_id:
        query = query.filter(StudentMaster.class_id == teacher.class_id)
    if teacher.section_1:
        query = query.filter(StudentMaster.section == teacher.section_1)
    students = query.order_by(StudentMaster.roll_no).all()
    return StudentListResponse(
        students=[StudentOut.model_validate(s) for s in students],
        total=len(students),
    )
