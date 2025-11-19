"""Kimlik doğrulama ve JWT token yönetimi."""

from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
import os

# JWT secret key - production'da environment variable'dan alınmalı
JWT_SECRET = os.environ.get("JWT_SECRET", secrets.token_urlsafe(32))
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24 * 7  # 7 gün

GEORGIA_TZ = timezone(timedelta(hours=4), name="UTC+4")


def hash_password(password: str) -> str:
    """Parolayı SHA-256 ile hash'le (PBKDF2 daha iyi ama basitlik için)."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    """Parola doğrulama."""
    return hash_password(password) == password_hash


def create_token(username: str) -> str:
    """JWT token oluştur."""
    now = datetime.now(GEORGIA_TZ)
    payload = {
        "username": username,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(hours=JWT_EXPIRATION_HOURS)).timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_token(token: str) -> Optional[str]:
    """JWT token doğrula ve username döndür."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload.get("username")
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

