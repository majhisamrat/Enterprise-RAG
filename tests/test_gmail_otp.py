import asyncio
import pytest
from app.utils.email_service import OTPService


def test_otp_generation_and_verification():
    email = "testuser@gmail.com"
    otp = OTPService.generate_otp()
    assert len(otp) == 6
    assert otp.isdigit()

    async def _test():
        from app.storage.redis_client import redis_manager
        await redis_manager.set_cache(f"otp:{email}", otp, ttl=300)

        verified = await OTPService.verify_otp(email, otp)
        assert verified is True

        verified_wrong = await OTPService.verify_otp(email, "000000")
        assert verified_wrong is False

    asyncio.run(_test())
