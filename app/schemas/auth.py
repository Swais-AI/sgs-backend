from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    teacher_id: int
    name: str
    email: str
    subject: str | None = None
    class_assigned: str | None = None
    section: str | None = None
    avatar_initials: str | None = None
    school_name: str | None = None
