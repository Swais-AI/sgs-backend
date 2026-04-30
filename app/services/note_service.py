from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.note import TeacherNote
from app.schemas.note import NoteCreate, NoteUpdate, NoteOut


def _to_out(note: TeacherNote) -> NoteOut:
    """Convert DB model → NoteOut (using frontend-compatible field names)."""
    return NoteOut(
        id=f"N{note.note_id}",
        title=note.title,
        content=note.content,
        chapter=note.chapter,
        contentType=note.content_type,
        canvasImageUrl=note.canvas_image_url,
        tags=note.tags or [],
        createdAt=note.created_at,
        updatedAt=note.updated_at,
    )


def get_notes(db: Session, teacher_id: int) -> List[NoteOut]:
    notes = (
        db.query(TeacherNote)
        .filter(TeacherNote.teacher_id == teacher_id)
        .order_by(TeacherNote.updated_at.desc())
        .all()
    )
    return [_to_out(n) for n in notes]


def get_note(db: Session, teacher_id: int, note_id: int) -> Optional[NoteOut]:
    note = db.query(TeacherNote).filter(
        TeacherNote.note_id == note_id,
        TeacherNote.teacher_id == teacher_id,
    ).first()
    return _to_out(note) if note else None


def create_note(db: Session, teacher_id: int, payload: NoteCreate) -> NoteOut:
    note = TeacherNote(
        teacher_id=teacher_id,
        title=payload.title,
        content=payload.content,
        chapter=payload.chapter,
        content_type=payload.content_type,
        canvas_image_url=payload.canvas_image_url,
        tags=payload.tags,
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return _to_out(note)


def update_note(db: Session, teacher_id: int, note_id: int, payload: NoteUpdate) -> Optional[NoteOut]:
    note = db.query(TeacherNote).filter(
        TeacherNote.note_id == note_id,
        TeacherNote.teacher_id == teacher_id,
    ).first()

    if not note:
        return None

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(note, field, value)

    db.commit()
    db.refresh(note)
    return _to_out(note)


def delete_note(db: Session, teacher_id: int, note_id: int) -> bool:
    note = db.query(TeacherNote).filter(
        TeacherNote.note_id == note_id,
        TeacherNote.teacher_id == teacher_id,
    ).first()

    if not note:
        return False

    db.delete(note)
    db.commit()
    return True
