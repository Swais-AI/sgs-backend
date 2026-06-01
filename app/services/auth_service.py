from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models.user import UserMaster
from app.models.teacher import TeacherMaster
from app.core.security import verify_password, create_access_token
from app.schemas.auth import LoginRequest, TokenResponse


def authenticate_teacher(db: Session, payload: LoginRequest) -> TokenResponse:
    # 1. Find user by email_id
    user = db.query(UserMaster).filter(
        UserMaster.email_id == payload.email,
        UserMaster.is_active == True,
    ).first()

    if not user or not verify_password(payload.password, user.password_hash):
        raise ValueError("Invalid email or password")

    # 2. Get teacher profile by matching email_id (no FK, linked by email)
    teacher: TeacherMaster = db.query(TeacherMaster).filter(
        TeacherMaster.email_id == user.email_id
    ).first()

    if not teacher:
        raise ValueError("No teacher profile found for this account")

    # 3. Issue JWT
    token = create_access_token(
        data={
            "sub": str(user.user_id),
            "teacher_id": teacher.teacher_id,
            "role": "teacher",
        }
    )

    avatar = (teacher.full_name or "SA")[:2].upper()

    # Resolve human-readable class name from sgs_class_master
    if teacher.class_id:
        row = db.execute(
            text("SELECT class_name FROM sgs_class_master WHERE class_id = :cid"),
            {"cid": teacher.class_id},
        ).fetchone()
        class_str = row[0] if row else str(teacher.class_id)
    else:
        class_str = None

    return TokenResponse(
        access_token=token,
        teacher_id=teacher.teacher_id,
        name=teacher.full_name or "",
        email=user.email_id,
        subject=teacher.subject_name,
        class_assigned=class_str,
        section=teacher.section_1,
        avatar_initials=avatar,
        school_name="SWAIS",
    )
