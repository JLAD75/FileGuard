"""
Extended database models for FileGuard v2.0
Includes: File versioning, sharing, folders, tags, 2FA, etc.
"""
import uuid
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    DateTime,
    ForeignKey,
    JSON,
    Integer,
    Text,
    BigInteger,
    Boolean,
    Index,
    Table,
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from .models import Base


# ==========================================
# Association Tables (Many-to-Many)
# ==========================================

# File Tags (Many-to-Many)
file_tags = Table(
    'file_tags',
    Base.metadata,
    Column('file_id', UUID(as_uuid=True), ForeignKey('file_metadata.id', ondelete='CASCADE'), primary_key=True),
    Column('tag_id', UUID(as_uuid=True), ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True),
)


# ==========================================
# Extended User Model Features
# ==========================================

class UserSettings(Base):
    """User preferences and settings"""
    __tablename__ = "user_settings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete='CASCADE'), unique=True, nullable=False)

    # 2FA Settings
    two_factor_enabled = Column(Boolean, default=False, nullable=False)
    two_factor_secret = Column(String, nullable=True)  # TOTP secret
    backup_codes = Column(JSON, nullable=True)  # List of backup codes

    # Preferences
    theme = Column(String, default="light", nullable=False)  # light, dark, auto
    language = Column(String, default="en", nullable=False)
    timezone = Column(String, default="UTC", nullable=False)
    email_notifications = Column(Boolean, default=True, nullable=False)

    # Storage quotas
    storage_quota_bytes = Column(BigInteger, default=10*1024*1024*1024, nullable=False)  # 10GB default
    storage_used_bytes = Column(BigInteger, default=0, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", backref="settings")


# ==========================================
# File Organization
# ==========================================

class Folder(Base):
    """Folder/directory structure for file organization"""
    __tablename__ = "folders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete='CASCADE'), nullable=False)
    parent_folder_id = Column(UUID(as_uuid=True), ForeignKey("folders.id", ondelete='CASCADE'), nullable=True)

    name_encrypted = Column(Text, nullable=False)  # Encrypted folder name
    path = Column(Text, nullable=False)  # Full path for quick lookups
    color = Column(String, nullable=True)  # UI color tag

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    owner = relationship("User", backref="folders")
    parent_folder = relationship("Folder", remote_side=[id], backref="subfolders")

    __table_args__ = (
        Index('idx_folder_owner_parent', 'owner_id', 'parent_folder_id'),
    )


# ==========================================
# File Versioning
# ==========================================

class FileVersion(Base):
    """File version history"""
    __tablename__ = "file_versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_id = Column(UUID(as_uuid=True), ForeignKey("file_metadata.id", ondelete='CASCADE'), nullable=False)

    version_number = Column(Integer, nullable=False)
    size_bytes = Column(BigInteger, nullable=False)
    storage_key = Column(Text, nullable=False)  # Storage location of this version

    # Metadata at time of version
    wrapped_dek = Column(Text, nullable=False)
    mime_type = Column(String, nullable=False)

    # Version metadata
    change_description = Column(Text, nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    file = relationship("FileMetadata", backref="versions")
    creator = relationship("User")

    __table_args__ = (
        Index('idx_version_file_number', 'file_id', 'version_number'),
    )


# ==========================================
# File Sharing & Permissions
# ==========================================

class FileShare(Base):
    """File sharing permissions"""
    __tablename__ = "file_shares"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_id = Column(UUID(as_uuid=True), ForeignKey("file_metadata.id", ondelete='CASCADE'), nullable=False)
    shared_with_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete='CASCADE'), nullable=False)
    shared_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Permissions
    permission_level = Column(String, nullable=False)  # view, download, edit, admin
    can_reshare = Column(Boolean, default=False, nullable=False)

    # Sharing metadata
    expires_at = Column(DateTime, nullable=True)  # Optional expiration
    access_count = Column(Integer, default=0, nullable=False)
    last_accessed_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    file = relationship("FileMetadata", backref="shares")
    shared_with = relationship("User", foreign_keys=[shared_with_user_id], backref="shared_files")
    shared_by = relationship("User", foreign_keys=[shared_by_user_id])

    __table_args__ = (
        Index('idx_share_user_file', 'shared_with_user_id', 'file_id'),
    )


class ShareLink(Base):
    """Public share links for files"""
    __tablename__ = "share_links"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_id = Column(UUID(as_uuid=True), ForeignKey("file_metadata.id", ondelete='CASCADE'), nullable=False)
    created_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Link configuration
    link_token = Column(String, unique=True, index=True, nullable=False)  # Random token for URL
    password_hash = Column(String, nullable=True)  # Optional password protection
    max_downloads = Column(Integer, nullable=True)  # Optional download limit
    download_count = Column(Integer, default=0, nullable=False)

    expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    last_accessed_at = Column(DateTime, nullable=True)

    # Relationships
    file = relationship("FileMetadata", backref="share_links")
    created_by = relationship("User")


# ==========================================
# Tags & Metadata
# ==========================================

class Tag(Base):
    """User-defined tags for file organization"""
    __tablename__ = "tags"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete='CASCADE'), nullable=False)

    name = Column(String, nullable=False)
    color = Column(String, nullable=True)  # Hex color code for UI

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    owner = relationship("User", backref="tags")

    __table_args__ = (
        Index('idx_tag_owner_name', 'owner_id', 'name'),
    )


# ==========================================
# Comments & Collaboration
# ==========================================

class FileComment(Base):
    """Comments on files for collaboration"""
    __tablename__ = "file_comments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_id = Column(UUID(as_uuid=True), ForeignKey("file_metadata.id", ondelete='CASCADE'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete='CASCADE'), nullable=False)
    parent_comment_id = Column(UUID(as_uuid=True), ForeignKey("file_comments.id", ondelete='CASCADE'), nullable=True)

    content = Column(Text, nullable=False)
    is_resolved = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    file = relationship("FileMetadata", backref="comments")
    user = relationship("User", backref="comments")
    parent_comment = relationship("FileComment", remote_side=[id], backref="replies")

    __table_args__ = (
        Index('idx_comment_file', 'file_id', 'created_at'),
    )


# ==========================================
# Notifications
# ==========================================

class Notification(Base):
    """User notifications"""
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete='CASCADE'), nullable=False)

    notification_type = Column(String, nullable=False)  # share, comment, scan_complete, etc.
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    link = Column(String, nullable=True)  # Optional link to related resource

    is_read = Column(Boolean, default=False, nullable=False)
    metadata = Column(JSON, nullable=True)  # Additional data

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", backref="notifications")

    __table_args__ = (
        Index('idx_notification_user_read', 'user_id', 'is_read', 'created_at'),
    )


# ==========================================
# Analytics & Metrics
# ==========================================

class FileAnalytics(Base):
    """File access analytics"""
    __tablename__ = "file_analytics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_id = Column(UUID(as_uuid=True), ForeignKey("file_metadata.id", ondelete='CASCADE'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete='SET NULL'), nullable=True)

    event_type = Column(String, nullable=False)  # view, download, share, edit
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    metadata = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    file = relationship("FileMetadata", backref="analytics")
    user = relationship("User")

    __table_args__ = (
        Index('idx_analytics_file_date', 'file_id', 'created_at'),
        Index('idx_analytics_user_date', 'user_id', 'created_at'),
    )


# ==========================================
# API Keys & Access Tokens
# ==========================================

class APIKey(Base):
    """API keys for programmatic access"""
    __tablename__ = "api_keys"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete='CASCADE'), nullable=False)

    name = Column(String, nullable=False)  # User-friendly name
    key_hash = Column(String, unique=True, index=True, nullable=False)  # Hashed API key
    key_prefix = Column(String, nullable=False)  # First few chars for identification

    scopes = Column(JSON, nullable=False)  # List of allowed operations
    is_active = Column(Boolean, default=True, nullable=False)

    last_used_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", backref="api_keys")

    __table_args__ = (
        Index('idx_apikey_user', 'user_id', 'is_active'),
    )
