from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone, timedelta
import secrets
from typing import Dict, List, Optional

from .exceptions import EntryNotFound


GEORGIA_TZ = timezone(timedelta(hours=4), name="UTC+4")


def _utcnow() -> str:
    return datetime.now(GEORGIA_TZ).replace(microsecond=0).isoformat()


@dataclass
class VaultEntry:
    service: str
    username: str
    password: str
    notes: str = ""
    tags: List[str] = field(default_factory=list)
    entry_id: str = field(default_factory=lambda: secrets.token_hex(12))
    created_at: str = field(default_factory=_utcnow)
    updated_at: str = field(default_factory=_utcnow)

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> "VaultEntry":
        return cls(**data)

    def update_password(self, password: str) -> None:
        self.password = password
        self.touch()

    def touch(self) -> None:
        self.updated_at = _utcnow()

    def matches(self, keyword: Optional[str]) -> bool:
        if not keyword:
            return True
        haystack = f"{self.service}|{self.username}|{' '.join(self.tags)}".lower()
        return keyword.lower() in haystack


class Vault:
    def __init__(self, entries: Optional[List[VaultEntry]] = None, meta: Optional[Dict] = None):
        self._entries: Dict[str, VaultEntry] = {
            entry.entry_id: entry for entry in (entries or [])
        }
        default_meta = {
            "created_at": _utcnow(),
            "updated_at": _utcnow(),
            "default_password_length": 24,
        }
        self.meta = meta or default_meta
        self.meta.setdefault("created_at", _utcnow())
        self.meta.setdefault("updated_at", _utcnow())

    def list_entries(self, keyword: Optional[str] = None) -> List[VaultEntry]:
        entries = [entry for entry in self._entries.values() if entry.matches(keyword)]
        return sorted(entries, key=lambda e: (e.service.lower(), e.username.lower()))

    def add_entry(self, entry: VaultEntry) -> VaultEntry:
        self._entries[entry.entry_id] = entry
        self.meta["updated_at"] = _utcnow()
        return entry

    def get_entry(self, entry_id: str) -> VaultEntry:
        try:
            return self._entries[entry_id]
        except KeyError as exc:
            raise EntryNotFound(f"Kayıt bulunamadı: {entry_id}") from exc

    def delete_entry(self, entry_id: str) -> VaultEntry:
        entry = self.get_entry(entry_id)
        del self._entries[entry_id]
        self.meta["updated_at"] = _utcnow()
        return entry

    def find_by_service(self, service: str) -> List[VaultEntry]:
        return [
            entry
            for entry in self._entries.values()
            if entry.service.lower() == service.lower()
        ]

    def to_dict(self) -> Dict:
        return {
            "entries": [entry.to_dict() for entry in self._entries.values()],
            "meta": self.meta,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Vault":
        entries = [VaultEntry.from_dict(item) for item in data.get("entries", [])]
        meta = data.get("meta", {})
        return cls(entries=entries, meta=meta)

