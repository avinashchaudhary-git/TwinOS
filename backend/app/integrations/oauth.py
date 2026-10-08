from cryptography.fernet import Fernet

from app.core.config import settings
from app.core.logging import logger


class TokenCrypto:
    """Provides Fernet-based symmetric encryption and decryption of OAuth tokens."""

    def __init__(self, key: str | None = None):
        raw_key = key or settings.ENCRYPTION_KEY
        try:
            self.fernet = Fernet(raw_key.encode("utf-8"))
        except Exception as e:
            logger.warning(
                f"Invalid Fernet key provided ({e}). Generating fallback key for session."
            )
            self.fernet = Fernet(Fernet.generate_key())

    def encrypt(self, plain_token: str) -> str:
        """Encrypts plaintext token string into base64 ciphertext."""
        if not plain_token:
            return ""
        encrypted_bytes = self.fernet.encrypt(plain_token.encode("utf-8"))
        return encrypted_bytes.decode("utf-8")

    def decrypt(self, cipher_token: str) -> str:
        """Decrypts base64 ciphertext back into plaintext token."""
        if not cipher_token:
            return ""
        try:
            decrypted_bytes = self.fernet.decrypt(cipher_token.encode("utf-8"))
            return decrypted_bytes.decode("utf-8")
        except Exception as e:
            logger.error(f"Failed to decrypt OAuth token: {e}")
            raise ValueError("Token decryption failed. Ensure ENCRYPTION_KEY is identical.")


token_crypto = TokenCrypto()


class GoogleOAuthService:
    """Manages Google OAuth2 authorization code exchange and token refresh."""

    AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    TOKEN_URL = "https://oauth2.googleapis.com/token"

    GMAIL_SCOPE = "https://www.googleapis.com/auth/gmail.readonly"
    CALENDAR_SCOPE = "https://www.googleapis.com/auth/calendar.readonly"

    @classmethod
    def get_authorization_url(cls, state: str, platform: str) -> str:
        scope = cls.GMAIL_SCOPE if platform == "gmail" else cls.CALENDAR_SCOPE
        params = [
            f"client_id={settings.GOOGLE_CLIENT_ID or 'mock_client_id'}",
            f"redirect_uri={settings.GOOGLE_REDIRECT_URI}",
            "response_type=code",
            f"scope={scope}",
            "access_type=offline",
            "prompt=consent",
            f"state={state}",
        ]
        return f"{cls.AUTH_URL}?{'&'.join(params)}"
