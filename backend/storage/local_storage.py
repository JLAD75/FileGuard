"""
Local filesystem storage backend implementation
Useful for development and small deployments
"""
import uuid
import os
import shutil
import aiofiles
from pathlib import Path
from typing import AsyncIterator

from .base import StorageBackend
from core.config import settings


class LocalStorage(StorageBackend):
    """Local filesystem storage backend"""

    def __init__(self):
        """Initialize local storage"""
        self.storage_path = Path(settings.storage_path)
        self._ensure_directory()

    def _ensure_directory(self):
        """Create storage directory if it doesn't exist"""
        self.storage_path.mkdir(parents=True, exist_ok=True)
        print(f"Local storage initialized at: {self.storage_path}")

    def _get_file_path(self, file_id: uuid.UUID, user_id: uuid.UUID) -> Path:
        """Get local file path"""
        user_dir = self.storage_path / "users" / str(user_id) / "files"
        user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir / str(file_id)

    def _get_chunk_path(
        self,
        file_id: uuid.UUID,
        chunk_number: int,
        user_id: uuid.UUID
    ) -> Path:
        """Get local chunk path"""
        chunks_dir = self.storage_path / "users" / str(user_id) / "chunks" / str(file_id)
        chunks_dir.mkdir(parents=True, exist_ok=True)
        return chunks_dir / f"{chunk_number:06d}"

    async def upload_chunk(
        self,
        file_id: uuid.UUID,
        chunk_number: int,
        chunk_data: bytes,
        user_id: uuid.UUID
    ) -> str:
        """Save chunk to local filesystem"""
        chunk_path = self._get_chunk_path(file_id, chunk_number, user_id)

        async with aiofiles.open(chunk_path, 'wb') as f:
            await f.write(chunk_data)

        return str(chunk_path)

    async def finalize_upload(
        self,
        file_id: uuid.UUID,
        total_chunks: int,
        user_id: uuid.UUID
    ) -> str:
        """Combine chunks into final file"""
        final_path = self._get_file_path(file_id, user_id)
        chunks_dir = self._get_chunk_path(file_id, 0, user_id).parent

        # Combine all chunks
        async with aiofiles.open(final_path, 'wb') as final_file:
            for chunk_num in range(total_chunks):
                chunk_path = self._get_chunk_path(file_id, chunk_num, user_id)

                if not chunk_path.exists():
                    raise Exception(f"Chunk {chunk_num} not found")

                async with aiofiles.open(chunk_path, 'rb') as chunk_file:
                    chunk_data = await chunk_file.read()
                    await final_file.write(chunk_data)

        # Clean up chunks directory
        try:
            shutil.rmtree(chunks_dir)
        except Exception as e:
            print(f"Warning: Failed to clean up chunks directory: {e}")

        return str(final_path)

    async def download_file(
        self,
        file_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> AsyncIterator[bytes]:
        """Download file as async stream"""
        file_path = self._get_file_path(file_id, user_id)

        if not file_path.exists():
            raise Exception(f"File not found: {file_id}")

        chunk_size = 64 * 1024  # 64KB chunks

        async with aiofiles.open(file_path, 'rb') as f:
            while True:
                chunk = await f.read(chunk_size)
                if not chunk:
                    break
                yield chunk

    async def delete_file(
        self,
        file_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> bool:
        """Delete file from local filesystem"""
        file_path = self._get_file_path(file_id, user_id)

        try:
            if file_path.exists():
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False

    async def get_file_size(
        self,
        file_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> int:
        """Get file size"""
        file_path = self._get_file_path(file_id, user_id)

        if not file_path.exists():
            raise Exception(f"File not found: {file_id}")

        return file_path.stat().st_size

    async def file_exists(
        self,
        file_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> bool:
        """Check if file exists"""
        file_path = self._get_file_path(file_id, user_id)
        return file_path.exists()

    async def copy_file(
        self,
        source_file_id: uuid.UUID,
        dest_file_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> bool:
        """Copy file for versioning"""
        source_path = self._get_file_path(source_file_id, user_id)
        dest_path = self._get_file_path(dest_file_id, user_id)

        try:
            if not source_path.exists():
                return False

            shutil.copy2(source_path, dest_path)
            return True
        except Exception as e:
            print(f"Error copying file: {e}")
            return False
