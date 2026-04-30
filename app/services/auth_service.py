from sqlalchemy.orm import Session

from app.models.user import UserMaster
from app.models.teacher import TeacherMaster
from app.core.security import verify_password, create_access_token
from app.schemas.auth import LoginRequest, TokenResponse


def authenticate_teacher(db: Session, payload: LoginRequest) -> TokenResponse:
    # 1. Find user by email
    user = db.query(UserMaster).filter(
        UserMaster.email == payload.email,
        UserMaster.is_active == True,
    ).first()

    if not user or not verify_password(payload.password, user.password_hash):
        raise ValueError("Invalid email or password")

    # 2. Get teacher profile
    teacher: TeacherMaster = user.teacher_profile
    if not teacher:
        raise ValueError("No teacher profile found for this account")

    # 3. Issue JWT — subject is "user_id:teacher_id" for easy lookup
    token = create_access_token(
        data={
            "sub": str(user.user_id),
            "teacher_id": teacher.teacher_id,
            "role": user.role.value,
        }
    )

    full_name = f"{teacher.first_name} {teacher.last_name}".strip()

    return TokenResponse(
        access_token=token,
        teacher_id=teacher.teacher_id,
        name=full_name,
        email=user.email,
        subject=teacher.subject,
        class_assigned=teacher.class_assigned,
        section=teacher.section,
        avatar_initials=teacher.avatar_initials,
        school_name=teacher.school_name,
    )
