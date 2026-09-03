"""
Which subjects a teacher is allowed to see.

Chapters, notes and study material are scoped through this, so a teacher sees
their own subject rather than every subject in the school.

The awkward part is that the same person has two identities:

    sgs_users_masters.user_id      3       (bigint)
    sgs_teacher_master.teacher_id  'T02'   (varchar)

and sgs_subject_master.teacher_id is a foreign key to *user_id*, not to the
teacher table. Email is the only thing linking the two rows, so that is what
we bridge on.

Resolution order:
  1. sgs_subject_master.teacher_id == the teacher's user_id  (the real
     assignment; requires a matching row in sgs_users_masters)
  2. sgs_subject_master.subject_name matched against the teacher's
     subject_name — a fallback for schools that never fill in the assignment
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.subject import SubjectMaster
from app.models.teacher import TeacherMaster
from app.models.user import UserMaster


def user_id_for(db: Session, teacher: TeacherMaster) -> Optional[int]:
    """The teacher's id in sgs_users_masters, matched on email."""
    email = (teacher.email_id or "").strip()
    if not email:
        return None
    row = (
        db.query(UserMaster.user_id)
        .filter(UserMaster.email_id.ilike(email))
        .first()
    )
    return row[0] if row else None


def subject_ids_for(db: Session, teacher: TeacherMaster) -> List[int]:
    """Subject ids this teacher teaches. Empty means nothing is assigned."""
    user_id = user_id_for(db, teacher)
    if user_id is not None:
        assigned = (
            db.query(SubjectMaster.subject_id)
            .filter(SubjectMaster.teacher_id == user_id)
            .all()
        )
        if assigned:
            return [row[0] for row in assigned]

    # No assignment row. Fall back to the subject named on the teacher record.
    name = (teacher.subject_name or "").strip()
    if not name:
        return []

    by_name = (
        db.query(SubjectMaster.subject_id)
        .filter(SubjectMaster.subject_name.ilike(name))
        .all()
    )
    return [row[0] for row in by_name]
