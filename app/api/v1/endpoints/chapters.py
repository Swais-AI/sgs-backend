from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_teacher
from app.db.session import get_db
from app.models.teacher import TeacherMaster
from app.models.chapter import SgsChapterContent

router = APIRouter(prefix="/chapters", tags=["chapters"])


@router.get("")
def get_chapters(
    teacher: TeacherMaster = Depends(get_current_teacher),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(SgsChapterContent)
        .filter(
            SgsChapterContent.chapter_id.isnot(None),
            SgsChapterContent.is_active == True,
            SgsChapterContent.record_status == "Active",
        )
        .order_by(SgsChapterContent.chapter_id)
        .all()
    )

    chapters = [
        {
            "chapter_id":    row.chapter_id,
            "chapter_name":  row.chapter_name,
            "content_title": row.content_title,
        }
        for row in rows
    ]

    return {"chapters": chapters}


@router.get("/{chapter_id}")
def get_chapter(
    chapter_id: int,
    teacher: TeacherMaster = Depends(get_current_teacher),
    db: Session = Depends(get_db),
):
    """Return a single chapter's full text content for the reading view."""
    row = (
        db.query(SgsChapterContent)
        .filter(
            SgsChapterContent.chapter_id == chapter_id,
            SgsChapterContent.is_active == True,
            SgsChapterContent.record_status == "Active",
        )
        .first()
    )
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chapter not found")

    return {
        "chapter_id":    row.chapter_id,
        "chapter_name":  row.chapter_name,
        "content_title": row.content_title,
        "content":       row.full_text_content or "",
    }
