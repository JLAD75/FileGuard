"""
Cleanup tasks for old files, temporary data, etc.
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, Any

from celery_app import celery_app
from core.config import settings
from core.database import SessionLocal
from core.models import FileMetadata, AuditLog
from storage import get_storage_backend

logger = logging.getLogger(__name__)


@celery_app.task(name="tasks.cleanup_old_files")
def cleanup_old_files_task(days: int = 90) -> Dict[str, Any]:
    """
    Clean up files that haven't been accessed in X days and are marked for deletion.

    Args:
        days: Number of days of inactivity before cleanup

    Returns:
        Dict with cleanup statistics
    """
    db = SessionLocal()
    deleted_count = 0
    failed_count = 0

    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Find files marked for deletion or very old incomplete uploads
        files_to_delete = db.query(FileMetadata).filter(
            (FileMetadata.upload_status == "failed") |
            ((FileMetadata.upload_status == "pending") & (FileMetadata.created_at < cutoff_date))
        ).all()

        storage = get_storage_backend()

        for file in files_to_delete:
            try:
                # Delete from storage
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                deleted = loop.run_until_complete(
                    storage.delete_file(file.id, file.owner_id)
                )
                loop.close()

                if deleted:
                    # Delete from database
                    db.delete(file)
                    deleted_count += 1
                    logger.info(f"Deleted file {file.id}")
                else:
                    failed_count += 1
                    logger.warning(f"Failed to delete file {file.id} from storage")

            except Exception as e:
                failed_count += 1
                logger.error(f"Error deleting file {file.id}: {e}")

        db.commit()

        # Log cleanup activity
        audit = AuditLog(
            user_id=None,
            action="system_cleanup",
            details={
                'deleted_files': deleted_count,
                'failed_deletions': failed_count,
                'cutoff_date': cutoff_date.isoformat()
            }
        )
        db.add(audit)
        db.commit()

        logger.info(f"Cleanup completed: {deleted_count} deleted, {failed_count} failed")

        return {
            'status': 'success',
            'deleted_count': deleted_count,
            'failed_count': failed_count
        }

    except Exception as e:
        logger.error(f"Cleanup task error: {e}")
        return {
            'status': 'error',
            'message': str(e),
            'deleted_count': deleted_count,
            'failed_count': failed_count
        }

    finally:
        db.close()
