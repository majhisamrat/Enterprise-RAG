from typing import Any, Dict, Optional
import httpx
from app.utils.logger import logger
from app.utils.exceptions import AuthenticationError


async def verify_google_id_token(id_token: str) -> Dict[str, Any]:
    """Verify Google ID token against Google's tokeninfo API."""
    url = f"https://oauth2.googleapis.com/tokeninfo?id_token={id_token}"
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(url)
            if response.status_code != 200:
                logger.error(f"Google ID token verification failed: {response.text}")
                raise AuthenticationError("Invalid or expired Google ID token")

            data = response.json()
            # Ensure email is present
            email = data.get("email")
            if not email:
                raise AuthenticationError("Google account has no verified email")

            return {
                "google_sub": data.get("sub"),
                "email": email.lower(),
                "name": data.get("name") or email.split("@")[0],
                "avatar": data.get("picture"),
                "email_verified": data.get("email_verified") == "true" or data.get("email_verified") is True,
            }
        except Exception as e:
            logger.error(f"Failed to verify Google token: {e}")
            raise AuthenticationError(f"Google authentication failed: {e}")
