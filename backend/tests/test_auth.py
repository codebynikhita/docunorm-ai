"""
Unit tests for enterprise cryptography, PBKDF2 hashing, and JWT tokens.
"""

import time
import pytest

from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_password_hashing_and_verification() -> None:
    """
    Verify BSI TR-02102 compliant PBKDF2 hashing and verification.
    """
    secret = "BaFinCompliance2026!"
    hashed = hash_password(secret)

    assert ":" in hashed
    assert verify_password(secret, hashed) is True
    assert verify_password("WrongPassword123!", hashed) is False
    assert verify_password("", hashed) is False


def test_jwt_token_lifecycle() -> None:
    """
    Verify RFC 7519 HMAC-SHA256 JWT generation, signature check, and payload retrieval.
    """
    payload = {
        "sub": "user-dora-test-uuid",
        "email": "dr.weber@siemens.de",
        "role": "auditor",
    }
    token = create_access_token(payload, expires_delta_seconds=3600)
    assert token.count(".") == 2

    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == "user-dora-test-uuid"
    assert decoded["email"] == "dr.weber@siemens.de"
    assert decoded["role"] == "auditor"


def test_jwt_token_expiration() -> None:
    """
    Verify that expired tokens are immediately rejected.
    """
    payload = {"sub": "expired-user"}
    # Token that expired 5 seconds ago
    token = create_access_token(payload, expires_delta_seconds=-5)
    decoded = decode_access_token(token)
    assert decoded is None


def test_jwt_tamper_detection() -> None:
    """
    Verify that tampering with token payload or signature is rejected.
    """
    token = create_access_token({"sub": "legit-user"}, expires_delta_seconds=3600)
    parts = token.split(".")
    # Tamper with signature
    tampered = f"{parts[0]}.{parts[1]}.badsignature"
    assert decode_access_token(tampered) is None
