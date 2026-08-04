"""Subject service — subjects scoped to a teacher's class."""

from typing import List
from sqlalchemy.orm import Session

from app.models.subject import SubjectMaster
from app.models.teacher import TeacherMaster
from app.schemas.subject import SubjectOut


def get_subjects(db: Session, teacher: TeacherMaster, class_id=None) -> List[SubjectOut]:
    """
    Subjects for the given class. Not restricted to the teacher's own class —
    when no class_id is passed every subject is returned, so a teacher with no
    class assigned still sees something.
    """
    query = db.query(SubjectMaster).filter(
        SubjectMaster.subject_name.isnot(None),
        SubjectMaster.subject_name != "",
        ~SubjectMaster.subject_name.ilike("TEST_%"),
    )
    if class_id is not None:
        query = query.filter(SubjectMaster.class_id == class_id)

    rows = query.order_by(SubjectMaster.subject_name).all()
    return [
        SubjectOut(
            subject_id=r.subject_id,
            subject_name=r.subject_name,
            subject_code=r.subject_code,
        )
        for r in rows
    ]
