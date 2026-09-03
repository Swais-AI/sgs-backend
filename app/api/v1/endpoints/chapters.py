from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_teacher
from app.db.session import get_db
from app.models.teacher import TeacherMaster
from app.models.chapter import SgsChapterContent
from app.models.chapter_master import ChapterMaster
from app.services.teacher_subjects import subject_ids_for

router = APIRouter(prefix="/chapters", tags=["chapters"])


def _serialise(master: ChapterMaster, has_content: bool) -> dict:
    return {
        "chapter_id":    master.chapter_id,
        "chapter_name":  master.chapter_name,
        "content_title": master.chapter_name,
        # The list comes from chapter_master, which includes chapters with no
        # content row yet. Saying so up front is better than a 404 when the
        # teacher opens one.
        "has_content":   has_content,
    }


@router.get("")
def get_chapters(
    subject_id: Optional[int] = Query(None, description="Filter chapters by subject"),
    teacher: TeacherMaster = Depends(get_current_teacher),
    db: Session = Depends(get_db),
):
    """
    Chapters for the subjects this teacher teaches.

    Scoping happens here rather than in the caller: the endpoint previously
    returned every chapter in the school whenever the client omitted
    subject_id, which meant any teacher could see any subject's material.
    """
    allowed = subject_ids_for(db, teacher)

    if not allowed:
        # No subject assignment we can resolve. Returning everything is how the
        # original leak happened, so return nothing and say why — the UI can
        # tell the teacher to have their subject assigned.
        return {"chapters": [], "reason": "no_subject_assigned"}

    if subject_id is not None and subject_id not in allowed:
        return {"chapters": [], "reason": "subject_not_assigned_to_teacher"}

    wanted = [subject_id] if subject_id is not None else allowed

    masters = (
        db.query(ChapterMaster)
        .filter(
            ChapterMaster.subject_id.in_(wanted),
            (ChapterMaster.record_status == "Active") | (ChapterMaster.record_status.is_(None)),
        )
        .order_by(ChapterMaster.chapter_no, ChapterMaster.chapter_id)
        .all()
    )

    # One query for which of these actually have readable content, so the list
    # can flag it without N round trips.
    ids = [m.chapter_id for m in masters]
    with_content = set()
    if ids:
        rows = (
            db.query(SgsChapterContent.chapter_id)
            .filter(
                SgsChapterContent.chapter_id.in_(ids),
                SgsChapterContent.is_active == True,
                SgsChapterContent.record_status == "Active",
            )
            .all()
        )
        with_content = {r[0] for r in rows}

    return {"chapters": [_serialise(m, m.chapter_id in with_content) for m in masters]}


@router.get("/{chapter_id}")
def get_chapter(
    chapter_id: int,
    teacher: TeacherMaster = Depends(get_current_teacher),
    db: Session = Depends(get_db),
):
    """Return a single chapter's full text content for the reading view."""
    master = db.query(ChapterMaster).filter(ChapterMaster.chapter_id == chapter_id).first()
    if not master:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chapter not found")

    # A chapter belonging to someone else's subject is not this teacher's to read.
    allowed = subject_ids_for(db, teacher)
    if master.subject_id not in allowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your subject")

    row = (
        db.query(SgsChapterContent)
        .filter(
            SgsChapterContent.chapter_id == chapter_id,
            SgsChapterContent.is_active == True,
            SgsChapterContent.record_status == "Active",
        )
        .first()
    )

    # The chapter exists but nobody has uploaded its text yet. That is a
    # content gap, not a missing chapter — 404 here made the UI look broken.
    if not row:
        return {
            "chapter_id":    master.chapter_id,
            "chapter_name":  master.chapter_name,
            "content_title": master.chapter_name,
            "content":       "",
            "has_content":   False,
        }

    return {
        "chapter_id":    row.chapter_id,
        "chapter_name":  row.chapter_name,
        "content_title": row.content_title,
        "content":       row.full_text_content or "",
        "has_content":   bool(row.full_text_content),
    }
