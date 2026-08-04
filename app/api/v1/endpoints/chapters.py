from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_teacher
from app.db.session import get_db
from app.models.teacher import TeacherMaster
from app.models.chapter import SgsChapterContent
from app.models.chapter_master import ChapterMaster

router = APIRouter(prefix="/chapters", tags=["chapters"])


@router.get("")
def get_chapters(
    subject_id: Optional[int] = Query(None, description="Filter chapters by subject"),
    teacher: TeacherMaster = Depends(get_current_teacher),
    db: Session = Depends(get_db),
):
    # Scoped by subject: source from chapter_master so chapters without a
    # content row (e.g. study-material only) still appear for selection.
    if subject_id is not None:
        masters = (
            db.query(ChapterMaster)
            .filter(
                ChapterMaster.subject_id == subject_id,
                (ChapterMaster.record_status == "Active") | (ChapterMaster.record_status.is_(None)),
            )
            .order_by(ChapterMaster.chapter_no, ChapterMaster.chapter_id)
            .all()
        )
        return {
            "chapters": [
                {
                    "chapter_id":    m.chapter_id,
                    "chapter_name":  m.chapter_name,
                    "content_title": m.chapter_name,
                }
                for m in masters
            ]
        }

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
