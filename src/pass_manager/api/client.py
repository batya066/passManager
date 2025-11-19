"""API client yardımcı fonksiyonları."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import requests

DEFAULT_CONFIG_PATH = Path.home() / ".pass_manager" / "api_config.json"


class APIClient:
    """API client sınıfı."""

    def __init__(self, api_url: str):
        self.api_url = api_url.rstrip("/")
        self.token: Optional[str] = None

    def register(self, username: str, password: str) -> dict:
        """Yeni kullanıcı kaydı."""
        response = requests.post(
            f"{self.api_url}/api/v1/auth/register",
            json={"username": username, "password": password},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        self.token = data["token"]
        return data

    def login(self, username: str, password: str) -> dict:
        """Kullanıcı girişi."""
        response = requests.post(
            f"{self.api_url}/api/v1/auth/login",
            json={"username": username, "password": password},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        self.token = data["token"]
        return data

    def save_config(self, config_path: Optional[Path] = None) -> None:
        """API konfigürasyonunu kaydet."""
        if not self.token:
            raise ValueError("Token yok, önce login yapın")
        config_path = config_path or DEFAULT_CONFIG_PATH
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config = {
            "api_url": self.api_url,
            "token": self.token,
        }
        with config_path.open("w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)

    @classmethod
    def load_config(cls, config_path: Optional[Path] = None) -> "APIClient":
        """Kaydedilmiş konfigürasyonu yükle."""
        config_path = config_path or DEFAULT_CONFIG_PATH
        if not config_path.exists():
            raise FileNotFoundError("API konfigürasyonu bulunamadı")
        with config_path.open("r", encoding="utf-8") as f:
            config = json.load(f)
        client = cls(config["api_url"])
        client.token = config["token"]
        return client


def setup_api_connection(api_url: str) -> APIClient:
    """API bağlantısını kur ve token al."""
    client = APIClient(api_url)
    print(f"API URL: {api_url}")
    print("\n1. Yeni kullanıcı kaydı")
    print("2. Mevcut kullanıcı girişi")
    choice = input("Seçiminiz (1/2): ").strip()

    if choice == "1":
        username = input("Kullanıcı adı: ").strip()
        password = input("Parola: ").strip()
        client.register(username, password)
        print("✓ Kayıt başarılı!")
    else:
        username = input("Kullanıcı adı: ").strip()
        password = input("Parola: ").strip()
        client.login(username, password)
        print("✓ Giriş başarılı!")

    client.save_config()
    print(f"✓ Konfigürasyon kaydedildi: {DEFAULT_CONFIG_PATH}")
    return client

