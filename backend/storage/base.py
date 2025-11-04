"""
Base storage backend interface
All storage implementations must inherit from this class
"""
from abc import ABC, abstractmethod
from typing import AsyncIterator, Optional
import uuid


class StorageBackend(ABC):
    """Abstract base class for storage backends"""

    @abstractmethod
    async def upload_chunk(
        self,
        file_id: uuid.UUID,
        chunk_number: int,
        chunk_data: bytes,
        user_id: uuid.UUID
    ) -> str:
        """
        Upload a file chunk to storage.

        Args:
            file_id: Unique identifier for the file
            chunk_number: Sequential chunk number (0-indexed)
            chunk_data: Raw chunk bytes
            user_id: User who owns the file

        Returns:
            Storage path or key for the chunk
        """
        pass

    @abstractmethod
    async def finalize_upload(
        self,
        file_id: uuid.UUID,
        total_chunks: int,
        user_id: uuid.UUID
    ) -> str:
        """
        Finalize multi-part upload by combining chunks.

        Args:
            file_id: Unique identifier for the file
            total_chunks: Total number of chunks
            user_id: User who owns the file

        Returns:
            Final storage path or key
        """
        pass

    @abstractmethod
    async def download_file(
        self,
        file_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> AsyncIterator[bytes]:
        """
        Download a file as async stream.

        Args:
            file_id: Unique identifier for the file
            user_id: User who owns the file

        Yields:
            Chunks of file data
        """
        pass

    @abstractmethod
    async def delete_file(
        self,
        file_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> bool:
        """
        Delete a file from storage.

        Args:
            file_id: Unique identifier for the file
            user_id: User who owns the file

        Returns:
            True if deleted successfully
        """
        pass

    @abstractmethod
    async def get_file_size(
        self,
        file_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> int:
        """
        Get the size of a stored file in bytes.

        Args:
            file_id: Unique identifier for the file
            user_id: User who owns the file

        Returns:
            File size in bytes
        """
        pass

    @abstractmethod
    async def file_exists(
        self,
        file_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> bool:
        """
        Check if a file exists in storage.

        Args:
            file_id: Unique identifier for the file
            user_id: User who owns the file

        Returns:
            True if file exists
        """
        pass

    @abstractmethod
    async def copy_file(
        self,
        source_file_id: uuid.UUID,
        dest_file_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> bool:
        """
        Copy a file (used for versioning).

        Args:
            source_file_id: Source file identifier
            dest_file_id: Destination file identifier
            user_id: User who owns the file

        Returns:
            True if copied successfully
        """
        pass

    def _get_file_key(self, file_id: uuid.UUID, user_id: uuid.UUID) -> str:
        """
        Generate storage key for a file.
        Format: users/{user_id}/files/{file_id}
        """
        return f"users/{user_id}/files/{file_id}"

    def _get_chunk_key(
        self,
        file_id: uuid.UUID,
        chunk_number: int,
        user_id: uuid.UUID
    ) -> str:
        """
        Generate storage key for a file chunk.
        Format: users/{user_id}/chunks/{file_id}/{chunk_number}
        """
        return f"users/{user_id}/chunks/{file_id}/{chunk_number:06d}"
