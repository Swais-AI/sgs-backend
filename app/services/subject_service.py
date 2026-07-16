"""Subject service — subjects scoped to a teacher's class."""

from typing import List
from sqlalchemy.orm import Session

from app.models.subject import SubjectMaster
from app.models.teacher import TeacherMaster
from app.schemas.subject import SubjectOut


def get_subjects(db: Session, teacher: TeacherMaster) -> List[SubjectOut]:
    """Return subjects for the teacher's class (empty if no class assigned)."""
    if not teacher.class_id:
        return []

    rows = (
        db.query(SubjectMaster)
        .filter(SubjectMaster.class_id == teacher.class_id)
        .order_by(SubjectMaster.subject_name)
        .all()
    )
    return [
        SubjectOut(
            subject_id=r.subject_id,
            subject_name=r.subject_name,
            subject_code=r.subject_code,
        )
        for r in rows
    ]
