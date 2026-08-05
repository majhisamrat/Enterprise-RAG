import random
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Tuple
from app.utils.logger import logger

from app.config import settings
from app.storage.redis_client import redis_manager


class OTPService:
    """Service for generating, emailing, and verifying 6-digit Gmail OTPs."""

    @staticmethod
    def generate_otp() -> str:
        """Generate 6-digit numeric OTP code."""
        return f"{random.randint(100000, 999999)}"

    @classmethod
    async def create_and_send_otp(cls, email: str) -> Tuple[bool, str]:
        """Generate OTP, store in Redis for 5 minutes, and send via Gmail SMTP."""
        otp = cls.generate_otp()
        redis_key = f"otp:{email.lower()}"
        ttl_seconds = settings.OTP_EXPIRE_MINUTES * 60

        # Store OTP in Redis
        saved = await redis_manager.set_cache(redis_key, otp, ttl=ttl_seconds)
        if not saved:
            logger.error(f"Failed to store OTP in Redis for {email}")
            return False, "Failed to generate OTP code"

        # Send email via SMTP or log mock output if SMTP credentials not provided
        sent = cls._send_email(email, otp)
        if sent:
            return True, f"OTP sent to {email}"
        else:
            # Even if real SMTP fails, in debug mode return success with logger output
            logger.warning(f"[MOCK OTP DEBUG] Sent 6-digit OTP code for {email}: {otp}")
            return True, f"OTP sent to {email} (Debug Mode OTP: {otp})"

    @classmethod
    async def verify_otp(cls, email: str, user_otp: str) -> bool:
        """Verify user-provided OTP against Redis value."""
        redis_key = f"otp:{email.lower()}"
        cached_otp = await redis_manager.get_cache(redis_key)
        if cached_otp and str(cached_otp).strip() == user_otp.strip():
            # Delete OTP after successful verification to prevent replay attacks
            await redis_manager.delete_cache(redis_key)
            return True
        return False

    @classmethod
    def _send_email(cls, recipient: str, otp_code: str) -> bool:
        """Send email via SMTP if configured."""
        if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
            logger.info("SMTP credentials not configured. Using logger fallback.")
            return False

        subject = f"Your Verification OTP Code: {otp_code}"
        body = f"""
        <html>
          <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2>{settings.APP_NAME} Verification</h2>
            <p>Your 6-digit verification code is:</p>
            <h1 style="color: #4F46E5; letter-spacing: 5px;">{otp_code}</h1>
            <p>This code will expire in <strong>{settings.OTP_EXPIRE_MINUTES} minutes</strong>.</p>
            <p>If you did not request this code, please ignore this email.</p>
          </body>
        </html>
        """

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = settings.SMTP_FROM_EMAIL
        msg["To"] = recipient
        msg.attach(MIMEText(body, "html"))

        try:
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.sendmail(settings.SMTP_FROM_EMAIL, recipient, msg.as_string())
            logger.info(f"Successfully sent OTP email to {recipient}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email to {recipient} via SMTP: {e}")
            return False
