"""
Storage backend factory
Returns the appropriate storage backend based on configuration
"""
from .base import StorageBackend
from .s3_storage import S3Storage
from .minio_storage import MinIOStorage
from .local_storage import LocalStorage
from core.config import settings


# Singleton instance
_storage_backend: StorageBackend = None


def get_storage_backend() -> StorageBackend:
    """
    Get the configured storage backend (singleton).

    Returns:
        StorageBackend instance based on settings.storage_backend
    """
    global _storage_backend

    if _storage_backend is not None:
        return _storage_backend

    backend_type = settings.storage_backend.lower()

    if backend_type == "s3":
        _storage_backend = S3Storage()
        print("Using S3 storage backend")
    elif backend_type == "minio":
        _storage_backend = MinIOStorage()
        print("Using MinIO storage backend")
    elif backend_type == "local":
        _storage_backend = LocalStorage()
        print("Using local filesystem storage backend")
    else:
        raise ValueError(
            f"Unknown storage backend: {backend_type}. "
            f"Valid options are: s3, minio, local"
        )

    return _storage_backend


def reset_storage_backend():
    """Reset the singleton instance (useful for testing)"""
    global _storage_backend
    _storage_backend = None
