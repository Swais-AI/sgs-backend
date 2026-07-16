from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_teacher
from app.models.teacher import TeacherMaster
from app.schemas.assignment import AssignmentListResponse, AssignmentCreate, AssignmentOut
from app.services import assignment_service

router = APIRouter(prefix="/assignments", tags=["assignments"])


@router.get("", response_model=AssignmentListResponse)
def list_assignments(
    teacher: TeacherMaster = Depends(get_current_teacher),
    db: Session = Depends(get_db),
):
    """Assignments for the teacher's class, with submission counts (dashboard widgets)."""
    items = assignment_service.get_assignments(db, teacher)
    return AssignmentListResponse(assignments=items, total=len(items))


@router.post("", response_model=AssignmentOut, status_code=status.HTTP_201_CREATED)
def create_assignment(
    payload: AssignmentCreate,
    teacher: TeacherMaster = Depends(get_current_teacher),
    db: Session = Depends(get_db),
):
    """Create an assignment for the teacher's class (Assign-work modal)."""
    return assignment_service.create_assignment(db, teacher, payload)
