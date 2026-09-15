"""
Student service — one definition of "a student on the roll".

The Students tab and the dashboard headcount used to filter differently: the
dashboard required is_active IS TRUE, the list applied no filter at all. The two
numbers therefore disagreed by however many inactive rows a class contained, and
teachers reported it as a bug. Both now go through `roll_query` so they cannot
drift apart again — change the rule here and both move together.

A note on is_active: the column DEFAULTS TO FALSE in the database. A student
created without it being set explicitly is inactive and will not appear here.
If students go missing from the Students tab, that is the cause, and the fix
belongs in whatever created them — not in loosening this filter.
"""

from sqlalchemy import or_
from sqlalchemy.orm import Query, Session

from app.models.student import StudentMaster


def roll_query(db: Session, class_id) -> Query:
    """Students counted as being on the roll for a class."""
    return db.query(StudentMaster).filter(
        StudentMaster.class_id == class_id,
        StudentMaster.is_active.is_(True),
        # NULL is treated as active: rows predating the column's use.
        or_(
            StudentMaster.record_status == "Active",
            StudentMaster.record_status.is_(None),
        ),
    )


def roll_count(db: Session, class_id) -> int:
    if not class_id:
        return 0
    return roll_query(db, class_id).count()
