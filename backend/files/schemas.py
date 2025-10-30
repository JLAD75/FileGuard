from pydantic import BaseModel
import uuid
from datetime import datetime

class FileMetadataBase(BaseModel):
    original_filename_encrypted: str
    size_bytes: int
    mime_type: str
    wrapped_dek: str

class FileMetadataCreate(FileMetadataBase):
    pass

class FileMetadata(FileMetadataBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    upload_status: str
    av_scan_status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True