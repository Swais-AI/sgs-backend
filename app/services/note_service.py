"""
Note service — stores rich note data as JSON in sgs_teacher_notes.notes column
since the sgs table has no separate title/chapter/content_type columns.
"""

import json
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.note import TeacherNote
from app.schemas.note import NoteCreate, NoteUpdate, NoteOut


def _to_out(note: TeacherNote) -> NoteOut:
    """Convert DB row → NoteOut, parsing the JSON blob stored in notes column."""
    try:
        data = json.loads(note.notes or "{}")
        if not isinstance(data, dict):
            data = {"content": str(note.notes)}
    except (json.JSONDecodeError, TypeError):
        data = {"content": note.notes or "", "title": "Note"}

    ts = note.created_at or datetime.now(timezone.utc)
    return NoteOut(
        id=f"N{note.notes_id}",
        title=data.get("title", ""),
        content=data.get("content"),
        chapter=data.get("chapter", ""),
        contentType=data.get("content_type", "typed"),
        canvasImageUrl=data.get("canvas_image_url"),
        tags=data.get("tags", []),
        createdAt=ts,
        updatedAt=ts,
    )


def get_notes(db: Session, teacher_id: int) -> List[NoteOut]:
    notes = (
        db.query(TeacherNote)
        .filter(TeacherNote.teacher_id == teacher_id)
        .order_by(TeacherNote.created_at.desc())
        .all()
    )
    return [_to_out(n) for n in notes]


def get_note(db: Session, teacher_id: int, note_id: int) -> Optional[NoteOut]:
    note = db.query(TeacherNote).filter(
        TeacherNote.notes_id == note_id,
        TeacherNote.teacher_id == teacher_id,
    ).first()
    return _to_out(note) if note else None


def create_note(db: Session, teacher_id: int, payload: NoteCreate) -> NoteOut:
    note = TeacherNote(
        teacher_id=teacher_id,
        notes=json.dumps({
            "title": payload.title,
            "content": payload.content,
            "chapter": payload.chapter,
            "content_type": payload.content_type.value if payload.content_type else "typed",
            "canvas_image_url": payload.canvas_image_url,
            "tags": payload.tags or [],
        }),
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return _to_out(note)


def update_note(db: Session, teacher_id: int, note_id: int, payload: NoteUpdate) -> Optional[NoteOut]:
    note = db.query(TeacherNote).filter(
        TeacherNote.notes_id == note_id,
        TeacherNote.teacher_id == teacher_id,
    ).first()

    if not note:
        return None

    try:
        existing = json.loads(note.notes or "{}")
        if not isinstance(existing, dict):
            existing = {}
    except (json.JSONDecodeError, TypeError):
        existing = {}

    update_data = payload.model_dump(exclude_unset=True)
    if "content_type" in update_data and update_data["content_type"] is not None:
        ct = update_data["content_type"]
        update_data["content_type"] = ct.value if hasattr(ct, "value") else ct
    existing.update(update_data)
    note.notes = json.dumps(existing)

    db.commit()
    db.refresh(note)
    return _to_out(note)


def delete_note(db: Session, teacher_id: int, note_id: int) -> bool:
    note = db.query(TeacherNote).filter(
        TeacherNote.notes_id == note_id,
        TeacherNote.teacher_id == teacher_id,
    ).first()

    if not note:
        return False

    db.delete(note)
    db.commit()
    return True
