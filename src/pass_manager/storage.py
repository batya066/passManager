from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from .crypto import decrypt_payload, encrypt_payload
from .exceptions import VaultAlreadyExists, VaultNotInitialized
from .models import Vault

DEFAULT_VAULT_PATH = Path.home() / ".pass_manager" / "vault.sec"


class VaultStorage:
    def __init__(self, path: Optional[str] = None):
        self.path = Path(path) if path else DEFAULT_VAULT_PATH

    def exists(self) -> bool:
        return self.path.exists()

    def read_envelope(self) -> dict:
        if not self.exists():
            raise VaultNotInitialized("Kasa dosyası bulunamadı.")
        with self.path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def write_envelope(self, envelope: dict) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = self.path.with_suffix(".tmp")
        with temp_path.open("w", encoding="utf-8") as handle:
            json.dump(envelope, handle, indent=2)
        temp_path.replace(self.path)


class SecureVault:
    def __init__(self, storage: VaultStorage):
        self.storage = storage

    def init_vault(self, master_password: str) -> Vault:
        if self.storage.exists():
            raise VaultAlreadyExists("Kasa zaten mevcut.")
        vault = Vault()
        envelope = encrypt_payload(master_password, vault.to_dict())
        self.storage.write_envelope(envelope)
        return vault

    def load_vault(self, master_password: str) -> Vault:
        envelope = self.storage.read_envelope()
        data = decrypt_payload(master_password, envelope)
        return Vault.from_dict(data)

    def save_vault(self, master_password: str, vault: Vault) -> None:
        envelope = encrypt_payload(master_password, vault.to_dict())
        self.storage.write_envelope(envelope)

