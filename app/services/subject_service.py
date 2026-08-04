"""Subject service — subjects scoped to a teacher's class."""

from typing import List
from sqlalchemy.orm import Session

from app.models.subject import SubjectMaster
from app.models.teacher import TeacherMaster
from app.schemas.subject import SubjectOut


def get_subjects(db: Session, teacher: TeacherMaster, class_id=None) -> List[SubjectOut]:
    """Subjects for the given class; falls back to the teacher's own class."""
    target_class = class_id if class_id is not None else teacher.class_id
    if not target_class:
        return []

    rows = (
        db.query(SubjectMaster)
        .filter(SubjectMaster.class_id == target_class)
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
