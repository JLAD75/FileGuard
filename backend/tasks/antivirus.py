"""
Antivirus scanning tasks using ClamAV
"""
import uuid
import logging
from typing import Dict, Any
import clamd

from celery_app import celery_app
from core.config import settings
from core.database import SessionLocal
from core.models import FileMetadata, AuditLog
from storage import get_storage_backend

logger = logging.getLogger(__name__)


class ClamAVScanner:
    """ClamAV scanner wrapper"""

    def __init__(self):
        """Initialize ClamAV connection"""
        if not settings.clamav_enabled:
            raise Exception("ClamAV is not enabled")

        self.client = clamd.ClamdNetworkSocket(
            host=settings.clamav_host,
            port=settings.clamav_port,
            timeout=settings.clamav_timeout
        )

    def ping(self) -> bool:
        """Check if ClamAV is responding"""
        try:
            return self.client.ping() == 'PONG'
        except Exception as e:
            logger.error(f"ClamAV ping failed: {e}")
            return False

    def scan_stream(self, data: bytes) -> Dict[str, Any]:
        """
        Scan data stream for viruses.

        Returns:
            Dict with 'status' (clean/infected) and optional 'virus_name'
        """
        try:
            result = self.client.instream(data)

            if result and 'stream' in result:
                scan_result = result['stream']

                # Parse result tuple: ('FOUND', 'virus_name') or ('OK', None)
                if scan_result[0] == 'OK':
                    return {'status': 'clean', 'virus_name': None}
                elif scan_result[0] == 'FOUND':
                    return {'status': 'infected', 'virus_name': scan_result[1]}
                else:
                    return {'status': 'error', 'message': str(scan_result)}
            else:
                return {'status': 'error', 'message': 'Unexpected scan result format'}

        except Exception as e:
            logger.error(f"ClamAV scan error: {e}")
            return {'status': 'error', 'message': str(e)}


@celery_app.task(name="tasks.scan_file", bind=True, max_retries=3)
def scan_file_task(self, file_id: str, user_id: str) -> Dict[str, Any]:
    """
    Scan a file for viruses using ClamAV.

    Args:
        file_id: UUID of the file to scan
        user_id: UUID of the file owner

    Returns:
        Dict with scan results
    """
    file_uuid = uuid.UUID(file_id)
    user_uuid = uuid.UUID(user_id)

    db = SessionLocal()

    try:
        # Get file metadata
        file_meta = db.query(FileMetadata).filter(
            FileMetadata.id == file_uuid
        ).first()

        if not file_meta:
            raise Exception(f"File not found: {file_id}")

        # Update status to scanning
        file_meta.av_scan_status = "scanning"
        db.commit()

        # Check if ClamAV is enabled
        if not settings.clamav_enabled:
            logger.warning("ClamAV is disabled, skipping scan")
            file_meta.av_scan_status = "skipped"
            file_meta.av_scan_result = "ClamAV disabled"
            db.commit()
            return {
                'file_id': file_id,
                'status': 'skipped',
                'message': 'ClamAV is disabled'
            }

        # Initialize scanner
        scanner = ClamAVScanner()

        # Check ClamAV availability
        if not scanner.ping():
            raise Exception("ClamAV is not responding")

        # Download file from storage
        storage = get_storage_backend()

        # Read file in chunks and scan
        file_data = b''
        async_gen = storage.download_file(file_uuid, user_uuid)

        # Convert async generator to sync (Celery limitation)
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            async def read_file():
                data = b''
                async for chunk in async_gen:
                    data += chunk
                return data

            file_data = loop.run_until_complete(read_file())
        finally:
            loop.close()

        # Scan the file
        scan_result = scanner.scan_stream(file_data)

        # Update database with results
        if scan_result['status'] == 'clean':
            file_meta.av_scan_status = 'clean'
            file_meta.av_scan_result = 'No threats detected'
            status_message = 'File is clean'

        elif scan_result['status'] == 'infected':
            file_meta.av_scan_status = 'infected'
            file_meta.av_scan_result = f"Virus found: {scan_result.get('virus_name', 'Unknown')}"
            status_message = f"Virus detected: {scan_result.get('virus_name')}"

            # Audit log for security event
            audit = AuditLog(
                user_id=user_uuid,
                action="file_scan_infected",
                details={
                    'file_id': str(file_uuid),
                    'virus_name': scan_result.get('virus_name'),
                    'severity': 'critical'
                }
            )
            db.add(audit)

        else:
            file_meta.av_scan_status = 'error'
            file_meta.av_scan_result = scan_result.get('message', 'Scan error')
            status_message = f"Scan error: {scan_result.get('message')}"

        db.commit()

        logger.info(f"File {file_id} scan completed: {status_message}")

        return {
            'file_id': file_id,
            'status': scan_result['status'],
            'message': status_message,
            'details': scan_result
        }

    except Exception as e:
        logger.error(f"Error scanning file {file_id}: {e}")

        # Update file status to error
        try:
            file_meta = db.query(FileMetadata).filter(
                FileMetadata.id == file_uuid
            ).first()
            if file_meta:
                file_meta.av_scan_status = 'error'
                file_meta.av_scan_result = f"Scan failed: {str(e)}"
                db.commit()
        except Exception:
            pass

        # Retry on failure
        raise self.retry(exc=e, countdown=60)  # Retry after 60 seconds

    finally:
        db.close()
