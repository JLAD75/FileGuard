"""
Celery tasks for FileGuard
"""
from .antivirus import scan_file_task
from .notifications import send_email_notification_task
from .cleanup import cleanup_old_files_task

__all__ = [
    "scan_file_task",
    "send_email_notification_task",
    "cleanup_old_files_task",
]
