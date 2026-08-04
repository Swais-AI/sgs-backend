from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_teacher
from app.db.session import get_db
from app.models.class_master import ClassMaster
from app.models.subject import SubjectMaster
from app.models.teacher import TeacherMaster

router = APIRouter(prefix="/classes", tags=["classes"])


@router.get("")
def list_classes(
    teacher: TeacherMaster = Depends(get_current_teacher),
    db: Session = Depends(get_db),
):
    """
    Classes any teacher can work with — not restricted to their own class.

    Only classes that actually have a subject are returned: a class with no
    subjects is a dead end (you could pick it but never reach a chapter), so
    listing it just produces empty dropdowns. As soon as a subject is added to
    a class it appears here automatically.
    """
    subject_classes = db.query(SubjectMaster.class_id).filter(SubjectMaster.class_id.isnot(None))

    rows = (
        db.query(ClassMaster)
        .filter(
            ClassMaster.class_name.isnot(None),
            ClassMaster.class_name != "",
            ~ClassMaster.class_name.ilike("TEST_%"),
            ClassMaster.class_id.in_(subject_classes),
        )
        .order_by(ClassMaster.class_name)
        .all()
    )

    classes = [
        {
            "class_id":   row.class_id,
            "class_name": row.class_name,
            "section":    row.section_name,
            "label":      f"{row.class_name}{' - ' + row.section_name if row.section_name else ''}",
        }
        for row in rows
    ]
    return {"classes": classes}
