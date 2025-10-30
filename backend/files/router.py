from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
import uuid

from . import schemas
from core import models
from core.database import get_db
from auth.dependencies import get_current_user

router = APIRouter()

import aiofiles

UPLOAD_DIR = "backend/uploads"

async def upload_chunk_to_storage(file_id: uuid.UUID, chunk: bytes):
    file_path = f"{UPLOAD_DIR}/{file_id}"
    async with aiofiles.open(file_path, "ab") as f:
        await f.write(chunk)
    return {"status": "ok"}


@router.post("/upload/init", response_model=schemas.FileMetadata)
def create_file_metadata(
    file_meta: schemas.FileMetadataCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    db_file = models.FileMetadata(**file_meta.model_dump(), owner_id=current_user.id)
    db.add(db_file)

    audit_log = models.AuditLog(
        user_id=current_user.id,
        action="file_upload_init",
        details={"file_id": str(db_file.id)},
    )
    db.add(audit_log)

    db.commit()
    db.refresh(db_file)
    return db_file


@router.post("/upload/{file_id}/chunk")
async def upload_file_chunk(
    file_id: uuid.UUID,
    chunk: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # Verify the file belongs to the current user
    db_file = db.query(models.FileMetadata).filter_by(id=file_id, owner_id=current_user.id).first()
    if not db_file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    # In a real implementation, you would stream the chunk to S3
    chunk_content = await chunk.read()
    await upload_chunk_to_storage(file_id, chunk_content)

    return {"status": "chunk received"}

@router.get("/", response_model=list[schemas.FileMetadata])
def list_files(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return db.query(models.FileMetadata).filter_by(owner_id=current_user.id).all()


from fastapi.responses import StreamingResponse
import io

from starlette.responses import FileResponse

@router.get("/download/{file_id}", response_class=FileResponse)
async def download_file(
    file_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    db_file = db.query(models.FileMetadata).filter_by(id=file_id, owner_id=current_user.id).first()
    if not db_file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    file_path = f"{UPLOAD_DIR}/{file_id}"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found on storage")

    # Audit log
    audit_log = models.AuditLog(
        user_id=current_user.id,
        action="file_download",
        details={"file_id": str(file_id)},
    )
    db.add(audit_log)
    db.commit()

    # In a real implementation, this would stream from S3/MinIO
    # For now, we'll stream a placeholder encrypted content
    async def fake_encrypted_content_generator():
        # This is a placeholder for the actual encrypted file content
        yield b"fake-encrypted-content"

    return StreamingResponse(fake_encrypted_content_generator(), media_type=db_file.mime_type)


@router.post("/upload/{file_id}/complete")
def mark_upload_as_complete(
    file_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    db_file = db.query(models.FileMetadata).filter_by(id=file_id, owner_id=current_user.id).first()
    if not db_file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    db_file.upload_status = "complete"

    # Audit log
    audit_log = models.AuditLog(
        user_id=current_user.id,
        action="file_upload_complete",
        details={"file_id": str(file_id)},
    )
    db.add(audit_log)

    db.commit()
    db.refresh(db_file)

    # Trigger antivirus scan task
    from tasks import scan_file
    scan_file.delay(str(file_id))

    return db_file