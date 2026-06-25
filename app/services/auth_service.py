from sqlalchemy.orm import Session

from app.models.user import UserMaster
from app.models.teacher import TeacherMaster
from app.models.assessment import Assessment
from app.core.security import verify_password, create_access_token
from app.schemas.auth import LoginRequest, TokenResponse


def _class_display(class_name: str) -> str:
    """Format a class number as ordinal grade: '8' → '8th Grade'."""
    try:
        n = int(class_name)
        if 10 <= n % 100 <= 20:
            suffix = "th"
        else:
            suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
        return f"{n}{suffix} Grade"
    except (ValueError, TypeError):
        return str(class_name)


def authenticate_teacher(db: Session, payload: LoginRequest) -> TokenResponse:
    # 1. Find user by login_id (email is used as login_id in sgs_users_masters)
    user = db.query(UserMaster).filter(
        UserMaster.login_id == payload.email,
        UserMaster.is_active == True,
    ).first()

    if not user or not verify_password(payload.password, user.password_hash):
        raise ValueError("Invalid email or password")

    # 2. Get teacher profile — linked by matching email_id (no FK in sgs schema)
    teacher = db.query(TeacherMaster).filter(
        TeacherMaster.email_id == user.login_id,
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

    # Resolve human-readable class name from assessments (class_id is a DB FK, not display name)
    assessment = db.query(Assessment).filter(
        Assessment.teacher_id == teacher.teacher_id
    ).first()
    class_display = (
        _class_display(assessment.class_name)
        if assessment and assessment.class_name
        else (_class_display(teacher.class_id) if teacher.class_id else None)
    )

    return TokenResponse(
        access_token=token,
        teacher_id=teacher.teacher_id,
        name=teacher.full_name,
        email=user.login_id,
        subject=teacher.subject_name,
        class_assigned=class_display,
        section=teacher.section_1,
        avatar_initials=None,
        school_name=None,
    )
