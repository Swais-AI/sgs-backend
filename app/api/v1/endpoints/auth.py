from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_teacher
from app.db.session import get_db
from app.models.teacher import TeacherMaster
from app.schemas.auth import LoginRequest, MeResponse, TokenResponse
from app.services.auth_service import authenticate_teacher

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """
    Teacher login.
    Returns JWT (1-day expiry) + teacher profile info.
    """
    try:
        return authenticate_teacher(db, payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        )


@router.get("/me", response_model=MeResponse)
def me(teacher: TeacherMaster = Depends(get_current_teacher)):
    """
    Returns the current teacher's profile from a valid JWT.
    Used by the faculty app on load to restore session from token.
    """
    return MeResponse(
        teacher_id=teacher.teacher_id,
        name=teacher.full_name,
        email=teacher.email_id,
        subject=teacher.subject_name,
        class_assigned=str(teacher.class_id) if teacher.class_id else None,
        section=teacher.section_1,
        avatar_initials=(teacher.full_name or "")[:2].upper() or None,
        school_name=None,
    )


@router.post("/logout")
def logout():
    """
    Client-side logout — just tell the client to drop the token.
    (Stateless JWT, no server-side invalidation needed for now.)
    """
    return {"message": "Logged out successfully"}
