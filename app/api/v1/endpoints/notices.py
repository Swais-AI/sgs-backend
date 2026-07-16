from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_teacher
from app.models.teacher import TeacherMaster
from app.schemas.notice import NoticeListResponse
from app.services import notice_service

router = APIRouter(prefix="/notices", tags=["notices"])


@router.get("", response_model=NoticeListResponse)
def list_notices(
    teacher: TeacherMaster = Depends(get_current_teacher),
    db: Session = Depends(get_db),
):
    """Recent announcements relevant to the teacher (read-only)."""
    items = notice_service.get_notices(db, teacher)
    return NoticeListResponse(notices=items, total=len(items))
