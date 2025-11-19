# Kişiye Özel Şifre Yöneticisi

Bu proje, güçlü kriptografi ve modern güvenlik ilkeleriyle tasarlanmış minimalist ama üst düzey korumalı bir şifre yöneticisidir. Tüm veriler tek bir kasada AES‑GCM ile şifrelenir, ana parola PBKDF2‑HMAC (SHA‑512) ile sertleştirilmiş bir anahtara dönüştürülür ve kasanın tamamı bütünlük kontrolüyle saklanır.

## Öne Çıkan Özellikler

- **Yerel ve Bulut Modları:** Hem yerel dosya hem de sunucu tabanlı kullanım desteği
- **Çoklu Cihaz Desteği:** Bilgisayar ve iOS cihazlardan aynı vault'a erişim
- **AES‑256‑GCM Şifreleme:** Yüksek iterasyonlu PBKDF2 ile anahtar türetme
- **Client-Side Encryption:** Veriler sunucuya gönderilmeden önce şifrelenir
- **JWT Authentication:** Güvenli token tabanlı kimlik doğrulama
- **Servis, kullanıcı adı, etiket ve not saklayabilen kayıt yapısı**
- **Güçlü parola üreticisi** (uzunluk, sembol seti, kolay okunur mod vb.)
- **CLI üzerinden hızlı komutlar:** `init`, `add`, `list`, `show`, `delete`, `generate`
- **REST API:** FastAPI ile modern web API desteği
- **Kasa dosyası yolu özelleştirilebilir;** varsayılan olarak `~/.pass_manager/vault.sec`
- **Tüm zaman damgaları Gürcistan yerel saatine (UTC+4) göre kaydedilir ve gösterilir**

## Kurulum

```bash
python -m venv .venv
.venv\Scripts\activate  # PowerShell
pip install -e .[dev]
```

## Kullanım

### Kasa Oluşturma

```bash
python -m pass_manager init
```

### Kayıt Ekleme

```bash
python -m pass_manager add --service github --username tanjiro
```

CLI, parola girmenizi ya da otomatik üretmenizi sağlar. Kayıt, şifrelenmiş kasaya eklenir.

### Kayıtları Listeleme

```bash
python -m pass_manager list
```

### Bir Kaydı Görüntüleme

```bash
python -m pass_manager show --id <ENTRY_ID>
```

### Parola Üretme

```bash
python -m pass_manager generate --length 28 --symbols hard
```

## Qt Tabanlı GUI

Grafik arayüz, CLI ile aynı güvenlik katmanlarını kullanır ve PySide6 sayesinde Windows/macOS/Linux üzerinde yerel görünümlü çalışır.

1. Uygulamayı başlatın:
   ```bash
   pass-manager-gui
   # veya
   python -m pass_manager.gui
   ```
2. Açılış diyaloğunda mevcut kasayı seçip ana parolayı girin ya da aynı ekrandan yeni bir kasa oluşturun.
3. Ana pencerede kayıtları tablo halinde görebilir, çift tıklayarak detay panelinde görüntüleyebilir, parolayı geçici olarak gösterebilir veya panoya kopyalayabilirsiniz (30 saniye sonra otomatik temizlenir).
4. “Kayıt Ekle” diyaloğu, CLI ile aynı parola üreticisini içerir; uzunluk/sembol seçeneklerini değiştirerek güvenli parolalar üretebilirsiniz.

GUI ve CLI aynı kasayı paylaşır; dilediğiniz zaman aralarında geçiş yapabilirsiniz.

## Güvenlik Notları

- Ana parolayı asla paylaşmayın; unutursanız kasayı kurtarmanın yolu yoktur.
- Kasa dosyasını düzenli olarak yedekleyin.
- CLI'yı kullanırken çıktıların terminal geçmişinden temizlendiğinden emin olun.

## 🌐 API Sunucu Modu (Çoklu Cihaz Desteği)

### Sunucu Kurulumu

1. **Bağımlılıkları yükleyin:**
   ```bash
   pip install -r requirements.txt
   ```

2. **API sunucusunu başlatın:**
   ```bash
   python start_server.py
   ```
   Sunucu `http://0.0.0.0:8000` adresinde çalışacaktır.

3. **API dokümantasyonu:** http://localhost:8000/docs

### CLI ile API Kullanımı

1. **API bağlantısını kurun:**
   ```bash
   pass-manager api-setup --api-url http://YOUR_SERVER_IP:8000
   ```

2. **API modunda komutları kullanın:**
   ```bash
   # Vault oluştur
   pass-manager --api init
   
   # Kayıt ekle
   pass-manager --api add --service github --username tanjiro --auto
   
   # Kayıtları listele
   pass-manager --api list
   ```

### Web Uygulaması (iOS, Android, Bilgisayar)

MacOS gerektirmez! `web_app/` klasöründe hazır bir web uygulaması var.

**Özellikler:**
- ✅ iOS, Android ve bilgisayardan erişilebilir
- ✅ Client-side encryption (Web Crypto API)
- ✅ Responsive tasarım
- ✅ PWA desteği (ana ekrana eklenebilir)

**Kurulum:**
```bash
cd web_app
python -m http.server 8080
```

Tarayıcıda `http://localhost:8080` adresini açın!

Detaylı bilgi için `web_app/README.md` ve `DEPLOYMENT.md` dosyalarına bakın.

### Güvenlik

- ✅ **Client-Side Encryption:** Tüm veriler client tarafında şifrelenir
- ✅ **Master Password Sunucuya Gönderilmez:** Sadece şifrelenmiş veriler sunucuda saklanır
- ✅ **JWT Token Authentication:** 7 günlük token süresi
- ✅ **Veri Bütünlüğü:** SHA3-256 checksum kontrolü

Detaylı API dokümantasyonu için `API_SETUP.md` dosyasına bakın.

## Test

```bash
pytest
```

*(Testler henüz eklenmedi; geliştirme sırasında eklenecektir.)*

