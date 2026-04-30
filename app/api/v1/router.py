from fastapi import APIRouter

from app.api.v1.endpoints import auth, notes, chapters

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(notes.router)
api_router.include_router(chapters.router)
