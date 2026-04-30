from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.auth import LoginRequest, TokenResponse
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


@router.post("/logout")
def logout():
    """
    Client-side logout — just tell the client to drop the token.
    (Stateless JWT, no server-side invalidation needed for now.)
    """
    return {"message": "Logged out successfully"}
