"""
MinIO storage backend implementation
"""
import uuid
import asyncio
from typing import AsyncIterator, Optional
from minio import Minio
from minio.error import S3Error
import io

from .base import StorageBackend
from core.config import settings


class MinIOStorage(StorageBackend):
    """MinIO storage backend"""

    def __init__(self):
        """Initialize MinIO client"""
        self.client = Minio(
            endpoint=settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure
        )
        self.bucket = settings.minio_bucket
        self._ensure_bucket()

    def _ensure_bucket(self):
        """Create bucket if it doesn't exist"""
        try:
            if not self.client.bucket_exists(self.bucket):
                self.client.make_bucket(self.bucket)
                print(f"Created MinIO bucket: {self.bucket}")
        except S3Error as e:
            print(f"Error ensuring bucket exists: {e}")
            raise

    async def upload_chunk(
        self,
        file_id: uuid.UUID,
        chunk_number: int,
        chunk_data: bytes,
        user_id: uuid.UUID
    ) -> str:
        """Upload a chunk to MinIO"""
        chunk_key = self._get_chunk_key(file_id, chunk_number, user_id)

        # MinIO client is sync, run in thread pool
        def _upload():
            data = io.BytesIO(chunk_data)
            self.client.put_object(
                bucket_name=self.bucket,
                object_name=chunk_key,
                data=data,
                length=len(chunk_data),
            )
            return chunk_key

        return await asyncio.to_thread(_upload)

    async def finalize_upload(
        self,
        file_id: uuid.UUID,
        total_chunks: int,
        user_id: uuid.UUID
    ) -> str:
        """Combine chunks into final file"""
        final_key = self._get_file_key(file_id, user_id)

        def _finalize():
            # Read all chunks and combine
            combined_data = io.BytesIO()

            for chunk_num in range(total_chunks):
                chunk_key = self._get_chunk_key(file_id, chunk_num, user_id)
                try:
                    response = self.client.get_object(self.bucket, chunk_key)
                    combined_data.write(response.read())
                    response.close()
                    response.release_conn()
                except S3Error as e:
                    raise Exception(f"Failed to read chunk {chunk_num}: {e}")

            # Upload combined file
            combined_data.seek(0)
            size = combined_data.getbuffer().nbytes
            self.client.put_object(
                bucket_name=self.bucket,
                object_name=final_key,
                data=combined_data,
                length=size,
            )

            # Clean up chunks
            for chunk_num in range(total_chunks):
                chunk_key = self._get_chunk_key(file_id, chunk_num, user_id)
                try:
                    self.client.remove_object(self.bucket, chunk_key)
                except S3Error:
                    pass  # Ignore errors during cleanup

            return final_key

        return await asyncio.to_thread(_finalize)

    async def download_file(
        self,
        file_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> AsyncIterator[bytes]:
        """Download file as async stream"""
        file_key = self._get_file_key(file_id, user_id)

        def _get_object():
            try:
                return self.client.get_object(self.bucket, file_key)
            except S3Error as e:
                raise Exception(f"File not found: {e}")

        response = await asyncio.to_thread(_get_object)

        try:
            # Stream in chunks
            chunk_size = 64 * 1024  # 64KB chunks
            while True:
                chunk = await asyncio.to_thread(response.read, chunk_size)
                if not chunk:
                    break
                yield chunk
        finally:
            response.close()
            response.release_conn()

    async def delete_file(
        self,
        file_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> bool:
        """Delete file from MinIO"""
        file_key = self._get_file_key(file_id, user_id)

        def _delete():
            try:
                self.client.remove_object(self.bucket, file_key)
                return True
            except S3Error as e:
                print(f"Error deleting file: {e}")
                return False

        return await asyncio.to_thread(_delete)

    async def get_file_size(
        self,
        file_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> int:
        """Get file size"""
        file_key = self._get_file_key(file_id, user_id)

        def _get_size():
            try:
                stat = self.client.stat_object(self.bucket, file_key)
                return stat.size
            except S3Error as e:
                raise Exception(f"File not found: {e}")

        return await asyncio.to_thread(_get_size)

    async def file_exists(
        self,
        file_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> bool:
        """Check if file exists"""
        file_key = self._get_file_key(file_id, user_id)

        def _exists():
            try:
                self.client.stat_object(self.bucket, file_key)
                return True
            except S3Error:
                return False

        return await asyncio.to_thread(_exists)

    async def copy_file(
        self,
        source_file_id: uuid.UUID,
        dest_file_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> bool:
        """Copy file for versioning"""
        source_key = self._get_file_key(source_file_id, user_id)
        dest_key = self._get_file_key(dest_file_id, user_id)

        def _copy():
            try:
                from minio.commonconfig import CopySource
                self.client.copy_object(
                    bucket_name=self.bucket,
                    object_name=dest_key,
                    source=CopySource(self.bucket, source_key)
                )
                return True
            except S3Error as e:
                print(f"Error copying file: {e}")
                return False

        return await asyncio.to_thread(_copy)
