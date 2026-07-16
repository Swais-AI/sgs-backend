"""Notice service — read-only school announcements relevant to a teacher."""

from typing import List
from sqlalchemy import or_, func
from sqlalchemy.orm import Session

from app.models.notice import NoticeBoard
from app.models.teacher import TeacherMaster
from app.schemas.notice import NoticeOut
from app.services.auth_service import get_class_context


def get_notices(db: Session, teacher: TeacherMaster, limit: int = 20) -> List[NoticeOut]:
    """
    Recent notices relevant to a teacher: school-wide ('all'), faculty-targeted,
    unscoped, or matching the teacher's class name. Read-only.
    """
    class_name, _ = get_class_context(db, teacher)

    conds = [
        func.lower(NoticeBoard.applicable_class) == "all",
        NoticeBoard.applicable_class.ilike("%faculty%"),
        NoticeBoard.applicable_class.is_(None),
    ]
    if class_name:
        conds.append(NoticeBoard.applicable_class.ilike(f"%{class_name}%"))

    rows = (
        db.query(NoticeBoard)
        .filter(or_(*conds))
        .order_by(NoticeBoard.notice_date.desc().nullslast())
        .limit(limit)
        .all()
    )
    return [
        NoticeOut(
            notice_id=r.notice_id,
            title=r.notice_title,
            text=r.notice_text,
            notice_date=r.notice_date,
            audience=r.applicable_class,
        )
        for r in rows
    ]
