"""
Chapters endpoint — returns the chapter list for the teacher's class/subject.
Currently returns static list from config; backend team can extend this
to query a chapters_master table when it's available.
"""

from fastapi import APIRouter, Depends

from app.api.deps import get_current_teacher
from app.models.teacher import TeacherMaster

router = APIRouter(prefix="/chapters", tags=["chapters"])

# Static chapter list for Class 8 Social Studies (Civic chapter set)
# TODO: Replace with DB query once chapters_master table is added by DB architect
CHAPTERS_CLASS_8_SS = [
    "Chapter 1 - The Indian Constitution",
    "Chapter 2 - Understanding Secularism",
    "Chapter 3 - Parliament and Laws",
    "Chapter 4 - Judiciary",
    "Chapter 5 - Understanding Marginalisation",
    "Chapter 6 - Confronting Marginalisation",
    "Chapter 7 - Public Facilities",
    "Chapter 8 - Law and Social Justice",
]


@router.get("")
def get_chapters(teacher: TeacherMaster = Depends(get_current_teacher)):
    """Return chapter list relevant to this teacher."""
    return {"chapters": CHAPTERS_CLASS_8_SS}
