class VaultError(Exception):
    """Genel kasa hatası."""


class VaultAlreadyExists(VaultError):
    """Kasa dosyası zaten mevcutken init çağrıldığında yükseltilir."""


class VaultNotInitialized(VaultError):
    """Kasa dosyası bulunamazsa yükseltilir."""


class VaultIntegrityError(VaultError):
    """Şifre çözme ya da bütünlük kontrolü başarısız olduğunda yükseltilir."""


class InvalidMasterPassword(VaultError):
    """Yanlış ana parola kullanıldığında yükseltilir."""


class EntryNotFound(VaultError):
    """İstenen kayıt bulunamadığında yükseltilir."""

