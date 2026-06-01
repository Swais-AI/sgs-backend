from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_teacher
from app.models.teacher    import TeacherMaster
from app.models.student    import StudentMaster
from app.models.assessment import Assessment, AssessmentResult
from app.schemas.report    import ReportResponse, StudentReportRow

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("", response_model=ReportResponse)
def get_report(
    teacher: TeacherMaster = Depends(get_current_teacher),
    db: Session = Depends(get_db),
):
    tid = teacher.teacher_id

    # Fetch students by class_id + section (same logic as students endpoint)
    student_query = db.query(StudentMaster).filter(StudentMaster.is_active == True)
    if teacher.class_id:
        student_query = student_query.filter(StudentMaster.class_id == teacher.class_id)
    if teacher.section_1:
        student_query = student_query.filter(StudentMaster.section == teacher.section_1)
    students = student_query.order_by(StudentMaster.roll_no).all()

    # Fetch this teacher's assessments
    assessments = db.query(Assessment).filter(Assessment.teacher_id == tid).all()
    assessment_ids = {a.assessment_id for a in assessments}
    total_assessments = len(assessments)
    max_marks_map = {a.assessment_id: float(a.max_marks) for a in assessments}

    # Fetch all results for these assessments in one query
    results_all = (
        db.query(AssessmentResult)
        .filter(AssessmentResult.assessment_id.in_(assessment_ids))
        .all()
        if assessment_ids else []
    )

    # Group results by student_id
    results_by_student: dict[int, list[AssessmentResult]] = {}
    for r in results_all:
        results_by_student.setdefault(r.student_id, []).append(r)

    rows: list[StudentReportRow] = []
    for student in students:
        student_results = results_by_student.get(student.student_id, [])
        marks_list = [
            float(r.marks_obtained)
            for r in student_results
            if r.marks_obtained is not None
        ]
        pct_list = [
            float(r.marks_obtained) / max_marks_map[r.assessment_id] * 100
            for r in student_results
            if r.marks_obtained is not None and r.assessment_id in max_marks_map
        ]

        avg_pct = round(sum(pct_list) / len(pct_list), 1) if pct_list else None
        avg_raw = round(sum(marks_list) / len(marks_list), 1) if marks_list else None

        rows.append(StudentReportRow(
            student_id=student.student_id,
            name=student.full_name or "",
            roll_number=student.roll_no or "",
            total_assessed=len(marks_list),
            average_marks=avg_raw,
            average_percent=avg_pct,
            highest_marks=max(marks_list) if marks_list else None,
            lowest_marks=min(marks_list) if marks_list else None,
            rank=0,
        ))

    rows.sort(key=lambda r: (-(r.average_percent or 0), r.roll_number))
    for i, row in enumerate(rows, start=1):
        row.rank = i

    # Resolve human-readable class name from sgs_class_master
    if teacher.class_id:
        row = db.execute(
            text("SELECT class_name FROM sgs_class_master WHERE class_id = :cid"),
            {"cid": teacher.class_id},
        ).fetchone()
        class_label = row[0] if row else str(teacher.class_id)
    else:
        class_label = "8th Grade"

    return ReportResponse(
        teacher_id=tid,
        class_name=class_label,
        section=teacher.section_1 or "A",
        total_students=len(students),
        total_assessments=total_assessments,
        students=rows,
    )
