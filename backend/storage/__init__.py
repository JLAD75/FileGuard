"""
Storage module for FileGuard
Provides abstraction for different storage backends (S3, MinIO, local)
"""

from .base import StorageBackend
from .factory import get_storage_backend
from .s3_storage import S3Storage
from .minio_storage import MinIOStorage
from .local_storage import LocalStorage

__all__ = [
    "StorageBackend",
    "get_storage_backend",
    "S3Storage",
    "MinIOStorage",
    "LocalStorage",
]
