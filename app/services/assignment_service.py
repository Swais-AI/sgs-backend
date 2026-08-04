"""Assignment service — list (with submission counts) + create."""

from datetime import datetime
from typing import List
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.assignment import AssignmentMaster, AssignmentResult
from app.models.subject import SubjectMaster
from app.models.student import StudentMaster
from app.models.teacher import TeacherMaster
from app.models.user import UserMaster
from app.schemas.assignment import AssignmentOut, AssignmentCreate


def _class_student_count(db: Session, class_id) -> int:
    if not class_id:
        return 0
    return (
        db.query(StudentMaster)
        .filter(StudentMaster.class_id == class_id, StudentMaster.is_active.is_(True))
        .count()
    )


def _subject_name(db: Session, subject_id) -> str | None:
    if not subject_id:
        return None
    s = db.query(SubjectMaster).filter(SubjectMaster.subject_id == subject_id).first()
    return s.subject_name if s else None


def _to_out(db: Session, a: AssignmentMaster, total_students: int) -> AssignmentOut:
    submitted = (
        db.query(AssignmentResult)
        .filter(
            AssignmentResult.assignment_id == a.assignment_id,
            AssignmentResult.submitted_at.isnot(None),
        )
        .count()
    )
    return AssignmentOut(
        assignment_id=a.assignment_id,
        title=a.assignment_title,
        subject=_subject_name(db, a.subject_id),
        chapter_id=a.chapter_id,
        due_date=a.due_date,
        submitted_count=submitted,
        total_students=total_students,
    )


def get_assignments(db: Session, teacher: TeacherMaster) -> List[AssignmentOut]:
    """All assignments for the teacher's class, with per-assignment submission counts."""
    if not teacher.class_id:
        return []
    total_students = _class_student_count(db, teacher.class_id)
    rows = (
        db.query(AssignmentMaster)
        .filter(AssignmentMaster.class_id == teacher.class_id)
        .order_by(AssignmentMaster.due_date.asc().nullslast())
        .all()
    )
    return [_to_out(db, a, total_students) for a in rows]


def _resolve_user_id(db: Session, teacher: TeacherMaster):
    """
    assigned_by has a FK to sgs_users_masters(user_id) — a different id space
    from teacher_id, so writing the teacher_id straight in violates the
    constraint. Match the teacher to their user row by email and fall back to
    NULL (the column is nullable) rather than failing the whole insert.
    """
    if not teacher.email_id:
        return None
    user = (
        db.query(UserMaster)
        .filter(func.lower(UserMaster.email_id) == teacher.email_id.lower())
        .first()
    )
    if not user:
        user = (
            db.query(UserMaster)
            .filter(func.lower(UserMaster.login_id) == teacher.email_id.lower())
            .first()
        )
    return user.user_id if user else None


def create_assignment(db: Session, teacher: TeacherMaster, payload: AssignmentCreate) -> AssignmentOut:
    """Create an assignment for the teacher's class (used by the Assign-work modal)."""
    assigned_by = _resolve_user_id(db, teacher)

    a = AssignmentMaster(
        assignment_title=payload.title,
        assignment_text=payload.text,
        subject_id=payload.subject_id,
        chapter_id=payload.chapter_id,
        due_date=payload.due_date,
        class_id=teacher.class_id,
        assigned_by=assigned_by,
        created_datetime=datetime.utcnow(),
        record_status="Active",
        version_no=1,
    )
    db.add(a)
    db.commit()
    db.refresh(a)
    return _to_out(db, a, _class_student_count(db, teacher.class_id))
