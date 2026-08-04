"""
Assignment attachments — optional worksheets/PDFs attached when assigning work.

Shares sgs_file_storage_metadata with chapter study material, distinguished by
entity_type = 'ASSIGNMENT_ATTACHMENT' (entity_id = assignment_id). Any file
type is accepted; delete is soft, matching the study-material behaviour.
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_teacher
from app.db.session import get_db
from app.models.assignment import AssignmentMaster
from app.models.file_storage import ENTITY_ASSIGNMENT_ATTACHMENT, FileStorageMetadata
from app.models.teacher import TeacherMaster
from app.services import s3_service

router = APIRouter(prefix="/assignments", tags=["assignment-files"])

MAX_BYTES = 50 * 1024 * 1024  # 50 MB — any file type


def _serialize(row: FileStorageMetadata) -> dict:
    return {
        "file_id":       row.file_id,
        "assignment_id": row.entity_id,
        "file_name":     row.file_name,
        "file_url":      row.file_url,
        "view_url":      s3_service.presign_get(row.file_url),
        "uploaded_by":   row.created_user_id,
        "uploaded_at":   row.created_at,
    }


@router.get("/{assignment_id}/files")
def list_assignment_files(
    assignment_id: int,
    teacher: TeacherMaster = Depends(get_current_teacher),
    db: Session = Depends(get_db),
):
    """Attachments for an assignment, each with a temporary view URL."""
    rows = (
        db.query(FileStorageMetadata)
        .filter(
            FileStorageMetadata.entity_type == ENTITY_ASSIGNMENT_ATTACHMENT,
            FileStorageMetadata.entity_id == assignment_id,
            FileStorageMetadata.record_status == "Active",
        )
        .order_by(FileStorageMetadata.created_at.desc())
        .all()
    )
    return {"files": [_serialize(r) for r in rows], "total": len(rows)}


@router.post("/{assignment_id}/files", status_code=status.HTTP_201_CREATED)
async def upload_assignment_file(
    assignment_id: int,
    file: UploadFile = File(...),
    teacher: TeacherMaster = Depends(get_current_teacher),
    db: Session = Depends(get_db),
):
    """Attach a file to an assignment. Optional — only called when one is picked."""
    assignment = (
        db.query(AssignmentMaster)
        .filter(AssignmentMaster.assignment_id == assignment_id)
        .first()
    )
    if not assignment:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Assignment not found")

    body = await file.read()
    if not body:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "The file is empty")
    if len(body) > MAX_BYTES:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "File too large (max 50 MB)")

    key = s3_service.build_assignment_key(assignment.class_id, assignment_id, file.filename)
    uri = s3_service.upload_file(body, key, file.content_type)

    record = FileStorageMetadata(
        entity_type=ENTITY_ASSIGNMENT_ATTACHMENT,
        entity_id=assignment_id,
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


@router.delete("/files/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_assignment_file(
    file_id: int,
    teacher: TeacherMaster = Depends(get_current_teacher),
    db: Session = Depends(get_db),
):
    """Soft-delete an attachment."""
    row = (
        db.query(FileStorageMetadata)
        .filter(
            FileStorageMetadata.file_id == file_id,
            FileStorageMetadata.entity_type == ENTITY_ASSIGNMENT_ATTACHMENT,
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
