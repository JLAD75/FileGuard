"""
AWS S3 storage backend implementation
"""
import uuid
import asyncio
from typing import AsyncIterator, Optional
import boto3
from botocore.exceptions import ClientError
import io

from .base import StorageBackend
from core.config import settings


class S3Storage(StorageBackend):
    """AWS S3 storage backend"""

    def __init__(self):
        """Initialize S3 client"""
        session = boto3.session.Session()

        s3_config = {
            'aws_access_key_id': settings.aws_access_key_id,
            'aws_secret_access_key': settings.aws_secret_access_key,
            'region_name': settings.aws_region,
        }

        if settings.s3_endpoint_url:
            s3_config['endpoint_url'] = settings.s3_endpoint_url

        self.client = session.client('s3', **s3_config)
        self.bucket = settings.s3_bucket
        self._ensure_bucket()

    def _ensure_bucket(self):
        """Create bucket if it doesn't exist"""
        try:
            self.client.head_bucket(Bucket=self.bucket)
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                # Bucket doesn't exist, create it
                try:
                    self.client.create_bucket(Bucket=self.bucket)
                    print(f"Created S3 bucket: {self.bucket}")
                except ClientError as create_error:
                    print(f"Error creating bucket: {create_error}")
                    raise
            else:
                raise

    async def upload_chunk(
        self,
        file_id: uuid.UUID,
        chunk_number: int,
        chunk_data: bytes,
        user_id: uuid.UUID
    ) -> str:
        """Upload a chunk to S3"""
        chunk_key = self._get_chunk_key(file_id, chunk_number, user_id)

        def _upload():
            self.client.put_object(
                Bucket=self.bucket,
                Key=chunk_key,
                Body=chunk_data
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
                    response = self.client.get_object(Bucket=self.bucket, Key=chunk_key)
                    combined_data.write(response['Body'].read())
                except ClientError as e:
                    raise Exception(f"Failed to read chunk {chunk_num}: {e}")

            # Upload combined file
            combined_data.seek(0)
            self.client.put_object(
                Bucket=self.bucket,
                Key=final_key,
                Body=combined_data.getvalue()
            )

            # Clean up chunks
            for chunk_num in range(total_chunks):
                chunk_key = self._get_chunk_key(file_id, chunk_num, user_id)
                try:
                    self.client.delete_object(Bucket=self.bucket, Key=chunk_key)
                except ClientError:
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
                return self.client.get_object(Bucket=self.bucket, Key=file_key)
            except ClientError as e:
                raise Exception(f"File not found: {e}")

        response = await asyncio.to_thread(_get_object)

        # Stream in chunks
        chunk_size = 64 * 1024  # 64KB chunks
        body = response['Body']

        try:
            while True:
                chunk = await asyncio.to_thread(body.read, chunk_size)
                if not chunk:
                    break
                yield chunk
        finally:
            body.close()

    async def delete_file(
        self,
        file_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> bool:
        """Delete file from S3"""
        file_key = self._get_file_key(file_id, user_id)

        def _delete():
            try:
                self.client.delete_object(Bucket=self.bucket, Key=file_key)
                return True
            except ClientError as e:
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
                response = self.client.head_object(Bucket=self.bucket, Key=file_key)
                return response['ContentLength']
            except ClientError as e:
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
                self.client.head_object(Bucket=self.bucket, Key=file_key)
                return True
            except ClientError:
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
                copy_source = {
                    'Bucket': self.bucket,
                    'Key': source_key
                }
                self.client.copy_object(
                    Bucket=self.bucket,
                    CopySource=copy_source,
                    Key=dest_key
                )
                return True
            except ClientError as e:
                print(f"Error copying file: {e}")
                return False

        return await asyncio.to_thread(_copy)
