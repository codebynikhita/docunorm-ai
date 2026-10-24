"""
Enterprise Cryptography & Authentication Security Module.
Implements BSI TR-02102 compliant PBKDF2-HMAC-SHA256 password hashing
and RFC 7519 HMAC-SHA256 JSON Web Token (JWT) state management.
"""

import base64
import hashlib
import hmac
import json
import secrets
import time
from typing import Any

from app.core.config import get_settings

settings = get_settings()


def hash_password(password: str) -> str:
    """
    Hashes a password using PBKDF2-HMAC-SHA256 with 100,000 iterations
    and a cryptographically secure 16-byte random salt.
    Format: <salt_hex>:<hash_hex>
    """
    salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(salt),
        100000,
    )
    return f"{salt}:{key.hex()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain password against a stored <salt_hex>:<hash_hex> string
    using constant-time comparison to prevent timing attacks.
    """
    try:
        salt, key_hex = hashed_password.split(":", 1)
        new_key = hashlib.pbkdf2_hmac(
            "sha256",
            plain_password.encode("utf-8"),
            bytes.fromhex(salt),
            100000,
        )
        return hmac.compare_digest(new_key.hex(), key_hex)
    except Exception:
        return False


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")


def _b64url_decode(s: str) -> bytes:
    padding = "=" * ((4 - len(s) % 4) % 4)
    return base64.urlsafe_b64decode((s + padding).encode("utf-8"))


def create_access_token(
    data: dict[str, Any],
    expires_delta_seconds: int = 86400 * 7,  # 7 days
) -> str:
    """
    Encodes an RFC 7519 compliant JSON Web Token with HMAC-SHA256 signature.
    """
    header = {"alg": "HS256", "typ": "JWT"}
    now = int(time.time())
    payload = {
        **data,
        "iat": now,
        "exp": now + expires_delta_seconds,
    }

    h_str = _b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    p_str = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    msg = f"{h_str}.{p_str}".encode("utf-8")
    sig = hmac.new(settings.SECRET_KEY.encode("utf-8"), msg, hashlib.sha256).digest()
    sig_str = _b64url_encode(sig)

    return f"{h_str}.{p_str}.{sig_str}"


def decode_access_token(token: str) -> dict[str, Any] | None:
    """
    Verifies and decodes an RFC 7519 JWT access token.
    Returns payload dictionary if valid and unexpired; None otherwise.
    """
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        h_str, p_str, sig_str = parts

        msg = f"{h_str}.{p_str}".encode("utf-8")
        expected_sig = hmac.new(settings.SECRET_KEY.encode("utf-8"), msg, hashlib.sha256).digest()
        actual_sig = _b64url_decode(sig_str)

        if not hmac.compare_digest(actual_sig, expected_sig):
            return None

        payload = json.loads(_b64url_decode(p_str).decode("utf-8"))
        if payload.get("exp", 0) < time.time():
            return None

        return payload
    except Exception:
        return None
