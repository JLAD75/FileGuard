import uuid
from datetime import datetime

from sqlalchemy import (
    create_engine,
    Column,
    String,
    DateTime,
    ForeignKey,
    JSON,
    Integer,
    Text,
    BigInteger,
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.dialects.postgresql import UUID

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    files = relationship("FileMetadata", back_populates="owner")
    audit_logs = relationship("AuditLog", back_populates="user")

class FileMetadata(Base):
    __tablename__ = "file_metadata"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Unencrypted metadata
    size_bytes = Column(BigInteger, nullable=False)
    mime_type = Column(String, nullable=False)
    original_filename_encrypted = Column(Text, nullable=False) # Encrypted original filename

    # Encrypted fields
    wrapped_dek = Column(Text, nullable=False) # Data Encryption Key wrapped with KEK

    # Status fields
    upload_status = Column(String, default="pending", nullable=False) # e.g., pending, complete, failed, scanning
    av_scan_status = Column(String, default="pending", nullable=False) # e.g., pending, clean, infected
    av_scan_result = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", back_populates="files")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True) # Can be null for system events
    action = Column(String, nullable=False) # e.g., 'user_login', 'file_upload', 'file_download'
    details = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="audit_logs")