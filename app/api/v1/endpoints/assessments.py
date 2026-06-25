from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_teacher
from app.models.teacher import TeacherMaster
from app.models.assessment import Assessment, AssessmentResult
from app.schemas.assessment import (
    AssessmentListResponse, AssessmentOut, AssessmentDetailOut, ResultOut
)

router = APIRouter(prefix="/assessments", tags=["assessments"])


def _build_out(a: Assessment) -> AssessmentOut:
    results_with_marks = [r for r in a.results if not r.is_absent and r.marks_obtained is not None]
    avg = (
        round(sum(float(r.marks_obtained) for r in results_with_marks) / len(results_with_marks), 1)
        if results_with_marks else None
    )
    return AssessmentOut(
        assessment_id=a.assessment_id,
        title=a.title,
        subject=a.subject,
        chapter=a.chapter,
        assessment_type=a.assessment_type,
        max_marks=float(a.max_marks),
        assessment_date=a.assessment_date,
        total_students=len(a.results),
        submitted=len(results_with_marks),
        class_average=avg,
    )


def _build_result(r: AssessmentResult, max_marks: float) -> ResultOut:
    pct = (
        round(float(r.marks_obtained) / max_marks * 100, 1)
        if r.marks_obtained is not None and not r.is_absent else None
    )
    return ResultOut(
        result_id=r.result_id,
        student_id=r.student_id,
        student_name=r.student_name,
        roll_number=r.roll_number,
        marks_obtained=float(r.marks_obtained) if r.marks_obtained is not None else None,
        max_marks=max_marks,
        percentage=pct,
    )


@router.get("", response_model=AssessmentListResponse)
def list_assessments(
    teacher: TeacherMaster = Depends(get_current_teacher),
    db: Session = Depends(get_db),
):
    assessments = (
        db.query(Assessment)
        .filter(Assessment.teacher_id == teacher.teacher_id)
        .order_by(Assessment.assessment_date.desc())
        .all()
    )
    return AssessmentListResponse(
        assessments=[_build_out(a) for a in assessments],
        total=len(assessments),
    )


@router.get("/{assessment_id}", response_model=AssessmentDetailOut)
def get_assessment(
    assessment_id: int,
    teacher: TeacherMaster = Depends(get_current_teacher),
    db: Session = Depends(get_db),
):
    a = db.query(Assessment).filter(
        Assessment.assessment_id == assessment_id,
        Assessment.teacher_id == teacher.teacher_id,
    ).first()
    if not a:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")

    max_marks = float(a.max_marks)
    out = _build_out(a)
    results = sorted(
        [_build_result(r, max_marks) for r in a.results],
        key=lambda x: x.roll_number,
    )
    return AssessmentDetailOut(**out.model_dump(), results=results)
