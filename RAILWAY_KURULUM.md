# 🚂 Railway.app - Adım Adım Kurulum Kılavuzu

## 📋 Ne Yapıyoruz?

Railway'a **TÜM PROJEYİ** yüklüyoruz. Bu şu demek:
- ✅ API sunucusu (Python FastAPI)
- ✅ Web uygulaması (HTML/CSS/JS)
- ✅ Veritabanı (SQLite - Railway'da otomatik)

**Sonuç:** Hem bilgisayardan hem telefondan aynı URL'den erişebilirsin!

---

## 🎯 ADIM 1: Railway'a Kayıt Ol

1. https://railway.app adresine git
2. "Start a New Project" butonuna tıkla
3. **GitHub ile giriş yap** (en kolay yol)
4. Railway hesabını oluştur

---

## 🎯 ADIM 2: Projeyi GitHub'a Yükle (Eğer yoksa)

### Eğer projen GitHub'da YOKSA:

**📖 DETAYLI KILAVUZ:** `GITHUB_KURULUM.md` dosyasına bak! Orada her şey adım adım anlatılmış.

**Kısa özet:**
1. GitHub'da yeni repository oluştur (https://github.com → "+" → "New repository")
2. Bilgisayarında PowerShell veya CMD aç:
```bash
cd C:\Users\Tanjiro\Documents\CODEX\passManager
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/KULLANICI_ADIN/repo_adi.git
git push -u origin main
```

**⚠️ ÖNEMLİ:** 
- `KULLANICI_ADIN` ve `repo_adi` kısımlarını kendi bilgilerinle değiştir!
- `git push` komutunda GitHub kullanıcı adı ve **Personal Access Token** isteyecek
- Normal parola değil, token gerekli! `GITHUB_KURULUM.md` dosyasında nasıl alınacağı anlatılmış

### Eğer projen GitHub'da VARSA:
Hiçbir şey yapma, devam et!

---

## 🎯 ADIM 3: Railway'a Projeyi Bağla

1. Railway dashboard'da **"New Project"** butonuna tıkla
2. **"Deploy from GitHub repo"** seçeneğini seç
3. GitHub'dan projeni seç
4. Railway otomatik olarak:
   - Projeyi algılar
   - Python olduğunu görür
   - Bağımlılıkları yükler
   - Sunucuyu başlatır

**⏱️ 2-3 dakika sürer, bekle!**

---

## 🎯 ADIM 4: Environment Variables (Gizli Ayarlar)

Railway dashboard'da projenin **"Variables"** sekmesine git:

1. **"New Variable"** butonuna tıkla
2. Şu değişkeni ekle:
   - **Name:** `JWT_SECRET`
   - **Value:** Rastgele bir şifre (örn: `my_super_secret_key_12345`)
3. **"Add"** butonuna tıkla

**Not:** JWT_SECRET çok önemli! Güçlü bir şifre kullan.

---

## 🎯 ADIM 5: Domain'i Al

1. Railway dashboard'da projenin **"Settings"** sekmesine git
2. **"Generate Domain"** butonuna tıkla
3. Railway sana bir domain verir, örneğin:
   - `pass-manager-production.up.railway.app`

**Bu domain'i not al!** Bu senin uygulamanın adresi.

---

## 🎯 ADIM 6: Test Et!

1. Tarayıcıda Railway'ın verdiği domain'i aç (örn: `https://pass-manager-production.up.railway.app`)
2. Web uygulaması açılmalı!
3. **"Kayıt Ol"** sekmesine git
4. Kullanıcı adı ve parola gir
5. **API URL** kısmına Railway domain'ini gir (otomatik dolu olmalı)
6. Kayıt ol!

---

## ✅ Artık Hazırsın!

### Bilgisayardan Kullanım:
1. Tarayıcıda Railway domain'ini aç
2. Giriş yap
3. Ana parolanı gir
4. Kullanmaya başla!

### Telefondan Kullanım:
1. Telefonun tarayıcısında Railway domain'ini aç
2. Giriş yap (aynı kullanıcı adı ve parola)
3. **Aynı ana parolayı gir** (çok önemli!)
4. Kullanmaya başla!

### iOS'ta Ana Ekrana Ekleme:
1. Safari'de uygulamayı aç
2. Alt kısımdaki **"Paylaş"** butonuna tıkla
3. **"Ana Ekrana Ekle"** seçeneğini seç
4. Artık uygulama gibi kullanabilirsin!

---

## 🔐 Önemli Notlar

### Master Password:
- **Her cihazda AYNI master password'ü kullanmalısın!**
- Master password farklı olursa veriler açılmaz
- Master password'ü unutursan veriler kaybolur (kurtarma yok!)

### Güvenlik:
- Railway otomatik HTTPS sağlar (güvenli)
- Veriler client-side şifrelenir (sunucu göremez)
- Master password sunucuya gönderilmez

### Kuzeninle Paylaşım:
- Kuzenin kendi kullanıcı adı ve parolasıyla kayıt olmalı
- Herkes kendi vault'unu kullanır
- Vault'lar birbirinden ayrıdır

---

## 🆘 Sorun mu Var?

### Uygulama açılmıyor:
- Railway dashboard'da **"Deployments"** sekmesine bak
- Hata var mı kontrol et
- Logları incele

### "API bağlantı hatası" alıyorum:
- API URL'in doğru olduğundan emin ol
- Railway domain'ini kullan (http://localhost:8000 değil!)
- HTTPS kullan (http:// değil, https://)

### Master password hatalı diyor:
- Her cihazda AYNI master password'ü kullandığından emin ol
- Büyük/küçük harf duyarlı!

---

## 📱 Kullanım Senaryosu

**Sen:**
1. Bilgisayardan Railway domain'ini aç
2. Giriş yap → Ana parola: `benim_sifrem_123`
3. Yeni şifre ekle

**Telefon:**
1. Telefondan AYNI Railway domain'ini aç
2. AYNI kullanıcı adı ve parola ile giriş yap
3. **AYNI ana parola:** `benim_sifrem_123`
4. Eklediğin şifreyi görürsün!

**Kuzenin:**
1. Kendi kullanıcı adı ve parolasıyla kayıt olur
2. Kendi master password'ünü belirler
3. Kendi vault'unu kullanır (seninkinden ayrı)

---

## 🎉 Başarılar!

Artık hem bilgisayardan hem telefondan şifrelerine erişebilirsin!

Sorun olursa Railway dashboard'daki logları kontrol et veya bana sor!

