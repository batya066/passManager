"""API request/response modelleri."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class UserCreate:
    """Kullanıcı oluşturma request modeli."""
    username: str
    password: str


@dataclass
class UserLogin:
    """Kullanıcı giriş request modeli."""
    username: str
    password: str


@dataclass
class VaultEnvelopeRequest:
    """Vault envelope gönderme request modeli."""
    encrypted_envelope: Dict[str, Any]


@dataclass
class VaultEnvelopeResponse:
    """Vault envelope response modeli."""
    encrypted_envelope: Dict[str, Any]
    updated_at: str


@dataclass
class EntryCreateRequest:
    """Yeni entry ekleme request modeli (encrypted envelope içinde)."""
    encrypted_envelope: Dict[str, Any]


@dataclass
class EntryUpdateRequest:
    """Entry güncelleme request modeli."""
    encrypted_envelope: Dict[str, Any]


@dataclass
class EntryDeleteRequest:
    """Entry silme request modeli."""
    encrypted_envelope: Dict[str, Any]

