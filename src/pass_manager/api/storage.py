"""API tabanlı vault storage adapter."""

from __future__ import annotations

import json
from typing import Optional

import requests

from ..crypto import decrypt_payload, encrypt_payload
from ..exceptions import VaultNotInitialized, VaultError
from ..models import Vault


class APIVaultStorage:
    """API üzerinden vault yönetimi."""

    def __init__(self, api_url: str, token: str):
        self.api_url = api_url.rstrip("/")
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    def _get_vault(self) -> dict:
        """Sunucudan vault'u al."""
        try:
            response = requests.get(
                f"{self.api_url}/api/v1/vault",
                headers=self.headers,
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
            envelope = data.get("encrypted_envelope", {})
            # Boş envelope kontrolü
            if not envelope or envelope == {}:
                raise VaultNotInitialized("Vault henüz oluşturulmamış.")
            return envelope
        except requests.exceptions.RequestException as e:
            raise VaultError(f"API bağlantı hatası: {e}") from e

    def _save_vault(self, envelope: dict) -> None:
        """Vault'u sunucuya kaydet."""
        try:
            response = requests.post(
                f"{self.api_url}/api/v1/vault",
                headers=self.headers,
                json={"encrypted_envelope": envelope},
                timeout=10,
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise VaultError(f"API kayıt hatası: {e}") from e

    def exists(self) -> bool:
        """Vault'un var olup olmadığını kontrol et."""
        try:
            self._get_vault()
            return True
        except (VaultNotInitialized, VaultError):
            return False

    def read_envelope(self) -> dict:
        """Şifrelenmiş envelope'u oku."""
        return self._get_vault()

    def write_envelope(self, envelope: dict) -> None:
        """Şifrelenmiş envelope'u yaz."""
        self._save_vault(envelope)


class SecureVaultAPI:
    """API tabanlı SecureVault wrapper."""

    def __init__(self, storage: APIVaultStorage):
        self.storage = storage

    def init_vault(self, master_password: str) -> Vault:
        """Yeni vault oluştur."""
        if self.storage.exists():
            from ..exceptions import VaultAlreadyExists
            raise VaultAlreadyExists("Vault zaten mevcut.")
        vault = Vault()
        envelope = encrypt_payload(master_password, vault.to_dict())
        self.storage.write_envelope(envelope)
        return vault

    def load_vault(self, master_password: str) -> Vault:
        """Vault'u yükle."""
        envelope = self.storage.read_envelope()
        data = decrypt_payload(master_password, envelope)
        return Vault.from_dict(data)

    def save_vault(self, master_password: str, vault: Vault) -> None:
        """Vault'u kaydet."""
        envelope = encrypt_payload(master_password, vault.to_dict())
        self.storage.write_envelope(envelope)

