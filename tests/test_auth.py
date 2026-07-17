# tests/test_auth.py
from datetime import UTC, datetime, timedelta

import jwt
import pytest
from fastapi import HTTPException

from auth import (
    JWT_ALGORITHM,
    JWT_SECRET_KEY,
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_hash_password_roundtrip():
    hashed = hash_password("correct-horse-battery-staple")

    assert hashed != "correct-horse-battery-staple"
    assert verify_password("correct-horse-battery-staple", hashed)
    assert not verify_password("wrong-password", hashed)


def test_create_and_decode_access_token():
    token = create_access_token({"sub": "admin", "role": "admin"})

    payload = decode_access_token(token)

    assert payload["sub"] == "admin"
    assert payload["role"] == "admin"


def test_decode_access_token_rejects_expired_token():
    expired_token = jwt.encode(
        {"sub": "admin", "role": "admin", "exp": datetime.now(UTC) - timedelta(minutes=1)},
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )

    with pytest.raises(HTTPException) as exc_info:
        decode_access_token(expired_token)

    assert exc_info.value.status_code == 401


def test_decode_access_token_rejects_bad_signature():
    forged_token = jwt.encode(
        {"sub": "admin", "role": "admin"}, "not-the-real-secret", algorithm=JWT_ALGORITHM
    )

    with pytest.raises(HTTPException) as exc_info:
        decode_access_token(forged_token)

    assert exc_info.value.status_code == 401
