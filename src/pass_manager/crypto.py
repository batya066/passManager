from __future__ import annotations

import base64
import hashlib
import json
import secrets
from typing import Any, Dict

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from .exceptions import InvalidMasterPassword, VaultIntegrityError

SALT_SIZE = 16
NONCE_SIZE = 12
KDF_ITERATIONS = 310_000


def _b64e(data: bytes) -> str:
    return base64.b64encode(data).decode("utf-8")


def _b64d(data: str) -> bytes:
    return base64.b64decode(data.encode("utf-8"))


def derive_key(master_password: str, salt: bytes, iterations: int = KDF_ITERATIONS) -> bytes:
    return hashlib.pbkdf2_hmac(
        "sha512", master_password.encode("utf-8"), salt, iterations, dklen=32
    )


def encrypt_payload(master_password: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    salt = secrets.token_bytes(SALT_SIZE)
    nonce = secrets.token_bytes(NONCE_SIZE)
    key = derive_key(master_password, salt)
    aesgcm = AESGCM(key)
    serialized = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    ciphertext = aesgcm.encrypt(nonce, serialized, None)
    checksum = hashlib.sha256(ciphertext).hexdigest()
    return {
        "version": 1,
        "kdf": {
            "name": "PBKDF2-HMAC-SHA512",
            "iterations": KDF_ITERATIONS,
            "salt": _b64e(salt),
        },
        "cipher": {
            "name": "AES-256-GCM",
            "nonce": _b64e(nonce),
            "payload": _b64e(ciphertext),
        },
        "checksum": checksum,
    }


def decrypt_payload(master_password: str, envelope: Dict[str, Any]) -> Dict[str, Any]:
    try:
        kdf = envelope["kdf"]
        cipher = envelope["cipher"]
        salt = _b64d(kdf["salt"])
        iterations = int(kdf["iterations"])
        nonce = _b64d(cipher["nonce"])
        ciphertext = _b64d(cipher["payload"])
        checksum = envelope.get("checksum")
    except (KeyError, ValueError) as exc:
        raise VaultIntegrityError("Kasa dosyası bozuk görünüyor.") from exc

    calculated_checksum = hashlib.sha3_256(ciphertext).hexdigest()
    if checksum != calculated_checksum:
        raise VaultIntegrityError("Kasa bütünlük doğrulamasından geçemedi.")

    key = derive_key(master_password, salt, iterations)
    aesgcm = AESGCM(key)
    try:
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    except InvalidTag as exc:
        raise InvalidMasterPassword("Ana parola hatalı veya veri bozulmuş.") from exc

    try:
        return json.loads(plaintext.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise VaultIntegrityError("Kasa verisi çözümlenemedi.") from exc

