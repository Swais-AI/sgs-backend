from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_teacher
from app.models.teacher import TeacherMaster
from app.schemas.note import NoteCreate, NoteUpdate, NoteOut, NoteListResponse
from app.services import note_service

router = APIRouter(prefix="/notes", tags=["notes"])


@router.get("", response_model=NoteListResponse)
def list_notes(
    teacher: TeacherMaster = Depends(get_current_teacher),
    db: Session = Depends(get_db),
):
    """Fetch all notes for the authenticated teacher."""
    notes = note_service.get_notes(db, teacher.teacher_id)
    return NoteListResponse(notes=notes, total=len(notes))


@router.post("", response_model=NoteOut, status_code=status.HTTP_201_CREATED)
def create_note(
    payload: NoteCreate,
    teacher: TeacherMaster = Depends(get_current_teacher),
    db: Session = Depends(get_db),
):
    """Create a new note (typed / voice / handwritten)."""
    return note_service.create_note(db, teacher.teacher_id, payload)


@router.get("/{note_id}", response_model=NoteOut)
def get_note(
    note_id: int,
    teacher: TeacherMaster = Depends(get_current_teacher),
    db: Session = Depends(get_db),
):
    note = note_service.get_note(db, teacher.teacher_id, note_id)
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return note


@router.put("/{note_id}", response_model=NoteOut)
def update_note(
    note_id: int,
    payload: NoteUpdate,
    teacher: TeacherMaster = Depends(get_current_teacher),
    db: Session = Depends(get_db),
):
    note = note_service.update_note(db, teacher.teacher_id, note_id, payload)
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return note


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(
    note_id: int,
    teacher: TeacherMaster = Depends(get_current_teacher),
    db: Session = Depends(get_db),
):
    deleted = note_service.delete_note(db, teacher.teacher_id, note_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
