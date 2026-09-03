"""
Which subjects a teacher is allowed to see.

Chapters, notes and study material are all scoped through this, so a teacher
sees their own subject rather than every subject in the school.

Two ways a teacher is linked to a subject, tried in order:
  1. sgs_subject_master.teacher_id — the explicit assignment
  2. sgs_teacher_master.subject_name matched against sgs_subject_master —
     a fallback for schools that fill in the teacher's subject as free text
     but never populate the assignment column
"""

from typing import List

from sqlalchemy import String, cast
from sqlalchemy.orm import Session

from app.models.subject import SubjectMaster
from app.models.teacher import TeacherMaster


def subject_ids_for(db: Session, teacher: TeacherMaster) -> List[int]:
    """Subject ids this teacher teaches. Empty means nothing is assigned."""
    # Both sides are cast to text before comparing. sgs_teacher_master.teacher_id
    # is varchar and holds values like 'T02', while sgs_subject_master.teacher_id
    # is bigint — comparing them directly makes Postgres try to parse 'T02' as a
    # number and raise, taking the whole endpoint down. Casting keeps this
    # working whichever way the column types are reconciled later.
    assigned = (
        db.query(SubjectMaster.subject_id)
        .filter(cast(SubjectMaster.teacher_id, String) == str(teacher.teacher_id))
        .all()
    )
    if assigned:
        return [row[0] for row in assigned]

    # Fallback: the teacher record carries a subject name but no assignment row.
    name = (teacher.subject_name or "").strip()
    if not name:
        return []

    by_name = (
        db.query(SubjectMaster.subject_id)
        .filter(SubjectMaster.subject_name.ilike(name))
        .all()
    )
    return [row[0] for row in by_name]
