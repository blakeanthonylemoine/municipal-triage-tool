# auth.py
"""Shared JWT + password hashing helpers.

Built for the admin login first, but deliberately principal-agnostic
(the token just carries a "role" claim) so tenant login can reuse the
same create/verify functions later instead of a second auth system.
"""
from datetime import datetime, timedelta, UTC

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from config import settings

JWT_SECRET_KEY = settings.jwt_secret_key
JWT_ALGORITHM = "HS256"
JWT_EXPIRES_MINUTES = 60 * 12

bearer_scheme = HTTPBearer()


def hash_password(plain_password: str) -> str:
    return bcrypt.hashpw(plain_password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


def create_access_token(claims: dict) -> str:
    payload = {**claims, "exp": datetime.now(UTC) + timedelta(minutes=JWT_EXPIRES_MINUTES)}
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")


def require_admin(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> dict:
    payload = decode_access_token(credentials.credentials)
    if payload.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return payload


def require_tenant(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> int:
    """Returns the authenticated tenant's id, derived from the token — never trust a tenant_id from the URL instead."""
    payload = decode_access_token(credentials.credentials)
    if payload.get("role") != "tenant":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant access required")
    return int(payload["sub"])
