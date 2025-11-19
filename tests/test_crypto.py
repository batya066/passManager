import pytest

from pass_manager.crypto import decrypt_payload, encrypt_payload
from pass_manager.exceptions import InvalidMasterPassword


def test_encrypt_decrypt_roundtrip():
    data = {"entries": [], "meta": {"created_at": "now", "updated_at": "now"}}
    envelope = encrypt_payload("StrongMaster!123", data)
    restored = decrypt_payload("StrongMaster!123", envelope)
    assert restored == data


def test_decrypt_with_wrong_password_fails():
    data = {"entries": [], "meta": {"created_at": "now", "updated_at": "now"}}
    envelope = encrypt_payload("CorrectHorseBattery", data)
    with pytest.raises(InvalidMasterPassword):
        decrypt_payload("WrongPassword", envelope)

