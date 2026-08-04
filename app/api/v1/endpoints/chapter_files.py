"""
Chapter study material (PDF) endpoints.

Files live in S3; sgs_file_storage_metadata holds the s3:// URI plus audit
columns. Replace/delete are soft — the old row is flipped to record_status
'Inactive' and its S3 object is retained until the year-end purge, so a wrong
upload can always be recovered.
"""

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_teacher
from app.db.session import get_db
from app.models.chapter_master import ChapterMaster
from app.models.file_storage import ENTITY_CHAPTER_STUDY_MATERIAL, FileStorageMetadata
from app.models.subject import SubjectMaster
from app.models.teacher import TeacherMaster
from app.services import s3_service

router = APIRouter(prefix="/chapters", tags=["chapter-files"])

MAX_BYTES = 50 * 1024 * 1024  # 50 MB — any file type is accepted


def _serialize(row: FileStorageMetadata) -> dict:
    return {
        "file_id":     row.file_id,
        "chapter_id":  row.entity_id,
        "file_name":   row.file_name,
        "file_url":    row.file_url,               # s3:// URI (internal)
        "view_url":    s3_service.presign_get(row.file_url),  # temporary https link
        "uploaded_by": row.created_user_id,
        "uploaded_at": row.created_at,
        "version_no":  row.version_no,
    }


def _chapter_context(db: Session, chapter_id: int) -> tuple[ChapterMaster, Optional[int], Optional[int]]:
    """Resolve chapter -> (chapter, subject_id, class_id) for the S3 key path."""
    chapter = db.query(ChapterMaster).filter(ChapterMaster.chapter_id == chapter_id).first()
    if not chapter:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Chapter not found")
    subject_id = chapter.subject_id
    class_id = None
    if subject_id:
        subject = db.query(SubjectMaster).filter(SubjectMaster.subject_id == subject_id).first()
        class_id = subject.class_id if subject else None
    return chapter, subject_id, class_id


async def _read_upload(file: UploadFile) -> bytes:
    """Any file type is allowed — only emptiness and size are checked."""
    body = await file.read()
    if not body:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "The file is empty")
    if len(body) > MAX_BYTES:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "File too large (max 50 MB)")
    return body


@router.get("/{chapter_id}/files")
def list_chapter_files(
    chapter_id: int,
    teacher: TeacherMaster = Depends(get_current_teacher),
    db: Session = Depends(get_db),
):
    """Active study material for a chapter, each with a temporary view URL."""
    rows = (
        db.query(FileStorageMetadata)
        .filter(
            FileStorageMetadata.entity_type == ENTITY_CHAPTER_STUDY_MATERIAL,
            FileStorageMetadata.entity_id == chapter_id,
            FileStorageMetadata.record_status == "Active",
        )
        .order_by(FileStorageMetadata.created_at.desc())
        .all()
    )
    return {"files": [_serialize(r) for r in rows], "total": len(rows)}


@router.post("/{chapter_id}/files", status_code=status.HTTP_201_CREATED)
async def upload_chapter_file(
    chapter_id: int,
    file: UploadFile = File(...),
    teacher: TeacherMaster = Depends(get_current_teacher),
    db: Session = Depends(get_db),
):
    """Upload a new PDF for a chapter (multiple files per chapter are allowed)."""
    _, subject_id, class_id = _chapter_context(db, chapter_id)
    body = await _read_upload(file)

    key = s3_service.build_key(class_id, subject_id, chapter_id, file.filename)
    uri = s3_service.upload_file(body, key, file.content_type)

    record = FileStorageMetadata(
        entity_type=ENTITY_CHAPTER_STUDY_MATERIAL,
        entity_id=chapter_id,
        file_name=file.filename,
        file_url=uri,
        created_at=datetime.now(timezone.utc),
        created_user_id=teacher.full_name or str(teacher.teacher_id),
        record_status="Active",
        version_no=1,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return _serialize(record)


@router.put("/files/{file_id}")
async def replace_chapter_file(
    file_id: int,
    file: UploadFile = File(...),
    teacher: TeacherMaster = Depends(get_current_teacher),
    db: Session = Depends(get_db),
):
    """Replace a file: the old row goes Inactive, a new Active row is created."""
    old = (
        db.query(FileStorageMetadata)
        .filter(
            FileStorageMetadata.file_id == file_id,
            FileStorageMetadata.entity_type == ENTITY_CHAPTER_STUDY_MATERIAL,
        )
        .first()
    )
    if not old:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "File not found")
    if old.record_status != "Active":
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "This file is no longer active")

    chapter_id = old.entity_id
    _, subject_id, class_id = _chapter_context(db, chapter_id)
    body = await _read_upload(file)

    key = s3_service.build_key(class_id, subject_id, chapter_id, file.filename)
    uri = s3_service.upload_file(body, key, file.content_type)

    now = datetime.now(timezone.utc)
    stamp = teacher.full_name or str(teacher.teacher_id)

    # Retire the old row — the S3 object stays until the year-end purge.
    old.record_status = "Inactive"
    old.modified_datetime = now
    old.modified_user_id = stamp
    old.updated_at = now

    record = FileStorageMetadata(
        entity_type=ENTITY_CHAPTER_STUDY_MATERIAL,
        entity_id=chapter_id,
        file_name=file.filename,
        file_url=uri,
        created_at=now,
        created_user_id=stamp,
        record_status="Active",
        version_no=(old.version_no or 1) + 1,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return _serialize(record)


@router.delete("/files/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_chapter_file(
    file_id: int,
    teacher: TeacherMaster = Depends(get_current_teacher),
    db: Session = Depends(get_db),
):
    """Soft-delete — hidden from listings, retained until the year-end purge."""
    row = (
        db.query(FileStorageMetadata)
        .filter(
            FileStorageMetadata.file_id == file_id,
            FileStorageMetadata.entity_type == ENTITY_CHAPTER_STUDY_MATERIAL,
        )
        .first()
    )
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "File not found")

    now = datetime.now(timezone.utc)
    row.record_status = "Inactive"
    row.modified_datetime = now
    row.modified_user_id = teacher.full_name or str(teacher.teacher_id)
    row.updated_at = now
    db.commit()
