from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_teacher
from app.models.teacher import TeacherMaster

router = APIRouter(prefix="/chapters", tags=["chapters"])


@router.get("")
def get_chapters(
    teacher: TeacherMaster = Depends(get_current_teacher),
    db: Session = Depends(get_db),
):
    """Return chapters from sgs_chapter_master for the teacher's class and subject."""
    rows = db.execute(text("""
        SELECT cm.chapter_name
        FROM sgs_chapter_master cm
        JOIN sgs_subject_master sm ON cm.subject_id = sm.subject_id
        WHERE sm.class_id = :class_id
          AND LOWER(sm.subject_name) = LOWER(:subject_name)
          AND (cm.record_status IS NULL OR cm.record_status = 'Active')
        ORDER BY cm.chapter_order, cm.chapter_no
    """), {
        "class_id": teacher.class_id,
        "subject_name": teacher.subject_name or "",
    }).fetchall()

    chapters = [r[0] for r in rows]
    return {"chapters": chapters}
