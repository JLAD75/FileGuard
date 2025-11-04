"""
Email notification tasks
"""
import logging
from typing import Dict, Any
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import aiosmtplib
import asyncio

from celery_app import celery_app
from core.config import settings

logger = logging.getLogger(__name__)


@celery_app.task(name="tasks.send_email_notification")
def send_email_notification_task(
    to_email: str,
    subject: str,
    body_html: str,
    body_text: str = None
) -> Dict[str, Any]:
    """
    Send email notification.

    Args:
        to_email: Recipient email address
        subject: Email subject
        body_html: HTML email body
        body_text: Plain text email body (optional)

    Returns:
        Dict with send status
    """
    if not settings.smtp_enabled:
        logger.warning("SMTP is disabled, email not sent")
        return {'status': 'skipped', 'message': 'SMTP disabled'}

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        async def send_email():
            # Create message
            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = f"{settings.smtp_from_name} <{settings.smtp_from_email}>"
            message['To'] = to_email

            # Add text parts
            if body_text:
                part1 = MIMEText(body_text, 'plain')
                message.attach(part1)

            part2 = MIMEText(body_html, 'html')
            message.attach(part2)

            # Send email
            await aiosmtplib.send(
                message,
                hostname=settings.smtp_host,
                port=settings.smtp_port,
                username=settings.smtp_user,
                password=settings.smtp_password,
                use_tls=True
            )

        loop.run_until_complete(send_email())
        loop.close()

        logger.info(f"Email sent to {to_email}: {subject}")
        return {'status': 'success', 'message': f'Email sent to {to_email}'}

    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return {'status': 'error', 'message': str(e)}
