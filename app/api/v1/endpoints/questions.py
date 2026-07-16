from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status

from app.api.deps import get_current_teacher
from app.models.teacher import TeacherMaster
from app.services import question_service

router = APIRouter(prefix="/questions", tags=["questions"])

_MAX_BYTES = 10 * 1024 * 1024  # 10 MB


@router.post("/extract")
async def extract_from_pdf(
    file: UploadFile = File(...),
    teacher: TeacherMaster = Depends(get_current_teacher),
):
    """Extract gradeable questions from an uploaded PDF question paper."""
    is_pdf = (file.content_type == "application/pdf") or (
        file.filename or ""
    ).lower().endswith(".pdf")
    if not is_pdf:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please upload a PDF file.")

    data = await file.read()
    if not data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The uploaded file is empty.")
    if len(data) > _MAX_BYTES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="PDF too large (max 10 MB).")

    try:
        questions = await question_service.extract_questions(data, teacher)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Couldn't read questions from this PDF. Try a text-based (not scanned) paper.",
        )

    return {"questions": questions, "total": len(questions)}
