# Pass Manager API Kurulum ve Kullanım Kılavuzu

## 🚀 Sunucu Kurulumu

### 1. Bağımlılıkları Yükleyin

```bash
pip install -r requirements.txt
```

### 2. API Sunucusunu Başlatın

```bash
python start_server.py
```

Sunucu `http://0.0.0.0:8000` adresinde çalışacaktır.

**Not:** Production ortamında HTTPS kullanın ve güvenlik ayarlarını yapın!

### 3. API Dokümantasyonu

Sunucu çalışırken şu adreslerden API dokümantasyonuna erişebilirsiniz:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📱 CLI Kullanımı

### API Bağlantısını Kurma

```bash
pass-manager api-setup --api-url http://YOUR_SERVER_IP:8000
```

Bu komut sizden:
1. Yeni kullanıcı kaydı veya mevcut kullanıcı girişi seçimi
2. Kullanıcı adı ve parola

isteyecektir. Token otomatik olarak kaydedilecektir.

### API ile Vault İşlemleri

Tüm normal komutlar `--api` flag'i ile API sunucusunu kullanır:

```bash
# Vault oluştur
pass-manager --api init

# Kayıt ekle
pass-manager --api add --service github --username tanjiro --auto

# Kayıtları listele
pass-manager --api list

# Kayıt göster
pass-manager --api show --id ENTRY_ID --reveal

# Kayıt sil
pass-manager --api delete --id ENTRY_ID
```

## 🔒 Güvenlik Özellikleri

### Client-Side Encryption

- Tüm veriler **client tarafında** şifrelenir (AES-256-GCM)
- Sunucu sadece şifrelenmiş verileri saklar
- Master password hiçbir zaman sunucuya gönderilmez
- PBKDF2-HMAC-SHA512 ile key derivation (310,000 iterasyon)

### Kimlik Doğrulama

- JWT token tabanlı authentication
- Token süresi: 7 gün
- Her istekte Bearer token ile doğrulama

### Veri Bütünlüğü

- SHA3-256 checksum ile veri bütünlüğü kontrolü
- Her vault güncellemesinde checksum doğrulanır

## 📱 Web Uygulaması (iOS, Android, Bilgisayar)

Swift yerine **web tabanlı bir uygulama** hazırladık! `web_app/` klasöründe bulabilirsiniz.

### Avantajları:
- ✅ **MacOS gerekmez** - Herhangi bir bilgisayardan geliştirebilirsiniz
- ✅ **iOS, Android ve bilgisayardan erişilebilir**
- ✅ **PWA desteği** - Ana ekrana eklenebilir
- ✅ **Client-side encryption** - Web Crypto API ile
- ✅ **Responsive design** - Mobil uyumlu

### Kullanım:
1. `web_app/` klasöründeki dosyaları bir web sunucusuna yükleyin
2. API URL'ini girin
3. Kullanmaya başlayın!

Detaylı kurulum için `web_app/README.md` dosyasına bakın.

### Eski Swift Örneği:
`ios_client_example.swift` dosyası hala mevcut ama artık gerekli değil.

### Önemli Notlar:

1. **Encryption Implementasyonu:** Python'daki `crypto.py` mantığını Swift'e uyarlamanız gerekiyor. CryptoKit framework'ünü kullanabilirsiniz.

2. **Network Security:** iOS'ta App Transport Security (ATS) ayarlarını yapmanız gerekebilir (development için).

3. **Token Storage:** Token'ı Keychain'de güvenli şekilde saklayın.

### iOS Encryption Örneği (CryptoKit ile):

```swift
import CryptoKit

// PBKDF2 key derivation
func deriveKey(password: String, salt: Data, iterations: Int) -> SymmetricKey {
    let passwordData = password.data(using: .utf8)!
    // CryptoKit'te PBKDF2 yok, CommonCrypto kullanmanız gerekebilir
    // veya CryptoSwift gibi bir kütüphane
}

// AES-GCM encryption
func encrypt(data: Data, key: SymmetricKey) throws -> (ciphertext: Data, nonce: AES.GCM.Nonce) {
    let nonce = AES.GCM.Nonce()
    let sealedBox = try AES.GCM.seal(data, using: key, nonce: nonce)
    return (sealedBox.ciphertext, nonce)
}
```

## 🌐 Production Deployment

### Öneriler:

1. **HTTPS:** Mutlaka SSL/TLS sertifikası kullanın (Let's Encrypt ücretsiz)
2. **Environment Variables:** JWT_SECRET ve database path'i environment variable'dan alın
3. **Database:** SQLite yerine PostgreSQL kullanın (daha fazla kullanıcı için)
4. **Rate Limiting:** API'ye rate limiting ekleyin
5. **CORS:** Production'da CORS ayarlarını spesifik domain'lerle sınırlayın
6. **Backup:** Düzenli veritabanı yedekleri alın

### Nginx Reverse Proxy Örneği:

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🔧 Sorun Giderme

### Token Süresi Doldu

Token süresi dolduğunda tekrar login yapmanız gerekir:

```bash
pass-manager api-setup --api-url http://YOUR_SERVER_IP:8000
```

### Bağlantı Hatası

- Sunucunun çalıştığından emin olun
- Firewall ayarlarını kontrol edin
- API URL'in doğru olduğundan emin olun

### Veri Senkronizasyonu

Her cihaz kendi master password'ü ile verileri decrypt eder. Master password'ler eşleşmeli!

## 📝 API Endpoints

- `POST /api/v1/auth/register` - Yeni kullanıcı kaydı
- `POST /api/v1/auth/login` - Kullanıcı girişi
- `GET /api/v1/vault` - Vault'u al
- `POST /api/v1/vault` - Vault'u kaydet/güncelle
- `GET /api/v1/health` - Sunucu sağlık kontrolü

## 🎯 Sonraki Adımlar

1. iOS uygulamasında encryption'ı implement edin
2. Production sunucusu kurun (HTTPS ile)
3. Veritabanını PostgreSQL'e migrate edin (opsiyonel)
4. Rate limiting ve monitoring ekleyin

