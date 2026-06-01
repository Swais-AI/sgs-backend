from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_teacher
from app.models.teacher import TeacherMaster
from app.models.lesson_plan import LessonPlan
from app.schemas.lesson_plan import (
    GenerateRequest, LessonPlanOut, LessonPlanListResponse, SaveRequest
)
from app.services import lesson_plan_service

router = APIRouter(prefix="/lesson-plans", tags=["lesson-plans"])


@router.post("/generate", response_model=LessonPlanOut)
async def generate_plan(
    payload: GenerateRequest,
    teacher: TeacherMaster = Depends(get_current_teacher),
):
    """Generate a lesson plan using AI (currently template-based)."""
    plan = await lesson_plan_service.generate(
        chapter=payload.chapter,
        topic=payload.topic,
        duration=payload.duration_minutes,
        custom_objectives=payload.objectives,
        special_notes=payload.special_notes,
        subject=teacher.subject_name or "Social Studies",
        class_name=str(teacher.class_id) if teacher.class_id else "8",
        section=teacher.section_1 or "A",
    )
    return LessonPlanOut(**plan)


@router.post("", response_model=LessonPlanOut, status_code=status.HTTP_201_CREATED)
def save_plan(
    payload: SaveRequest,
    teacher: TeacherMaster = Depends(get_current_teacher),
    db: Session = Depends(get_db),
):
    """Save a generated lesson plan to the database."""
    p = payload.plan
    record = LessonPlan(
        teacher_id=teacher.teacher_id,
        title=p.title,
        subject=p.subject,
        class_name=p.class_name,
        section=p.section,
        chapter_text=p.chapter_text,
        duration_minutes=p.duration_minutes,
        objectives=p.objectives,
        materials=p.materials,
        core_concept=p.core_concept,
        plan_sections=p.plan_sections,
        assessment_method=p.assessment_method,
        homework=p.homework,
        differentiation=p.differentiation,
        modification_log=[],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        record_status="Active",
        version_no=1,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return LessonPlanOut.model_validate(record)


@router.get("", response_model=LessonPlanListResponse)
def list_plans(
    teacher: TeacherMaster = Depends(get_current_teacher),
    db: Session = Depends(get_db),
):
    """List all saved lesson plans for this teacher."""
    plans = (
        db.query(LessonPlan)
        .filter(
            LessonPlan.teacher_id == teacher.teacher_id,
            LessonPlan.record_status == "Active",
        )
        .order_by(LessonPlan.created_at.desc())
        .all()
    )
    return LessonPlanListResponse(
        plans=[LessonPlanOut.model_validate(p) for p in plans],
        total=len(plans),
    )


@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_plan(
    plan_id: int,
    teacher: TeacherMaster = Depends(get_current_teacher),
    db: Session = Depends(get_db),
):
    """Soft-delete a lesson plan."""
    plan = db.query(LessonPlan).filter(
        LessonPlan.lesson_plan_id == plan_id,
        LessonPlan.teacher_id == teacher.teacher_id,
    ).first()
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
    plan.record_status = "Deleted"
    db.commit()
