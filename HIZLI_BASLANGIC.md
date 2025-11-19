# 🚀 Hızlı Başlangıç Kılavuzu

## 1️⃣ Ücretsiz Sunucu Seçenekleri

### Railway.app (ÖNERİLEN) ⭐
1. https://railway.app adresine git
2. GitHub ile giriş yap
3. "New Project" > "Deploy from GitHub repo"
4. Reponu seç
5. **Bitti!** Otomatik olarak deploy edilir

**Avantajlar:**
- $5 ücretsiz kredi/ay (yeterli)
- Otomatik HTTPS
- Çok kolay kurulum

### Render.com (Alternatif)
1. https://render.com adresine git
2. "New +" > "Web Service"
3. GitHub reponu bağla
4. Build: `pip install -r requirements.txt`
5. Start: `python start_server.py`

## 2️⃣ Web Uygulamasını Çalıştır

### Yerel Test:
```bash
cd web_app
python -m http.server 8080
```

Tarayıcıda `http://localhost:8080` açın!

### Production:
Web uygulamasını herhangi bir statik hosting'e yükleyin:
- GitHub Pages (ücretsiz)
- Netlify (ücretsiz)
- Vercel (ücretsiz)
- Veya kendi sunucunuz

## 3️⃣ API URL'ini Ayarla

Web uygulamasında API URL'ini girin:
- Railway: `https://your-app.railway.app`
- Render: `https://your-app.onrender.com`
- Yerel: `http://localhost:8000`

## 4️⃣ Kullanmaya Başla!

1. Web uygulamasında kayıt ol veya giriş yap
2. Ana parolanı gir
3. Vault'unu kullan!

## 📱 iOS/Android'de Kullanım

1. Web uygulamasını tarayıcıda aç
2. Safari'de (iOS) veya Chrome'da (Android) "Paylaş" > "Ana Ekrana Ekle"
3. Artık uygulama gibi kullanabilirsin!

## ⚠️ Önemli Notlar

- **Master Password:** Her cihazda aynı master password'ü kullanmalısın
- **API URL:** Web uygulamasında doğru API URL'ini girdiğinden emin ol
- **HTTPS:** Production'da mutlaka HTTPS kullan

## 🆘 Sorun mu var?

- API çalışmıyor mu? `DEPLOYMENT.md` dosyasına bak
- Web uygulaması çalışmıyor mu? `web_app/README.md` dosyasına bak
- Genel sorular? `API_SETUP.md` dosyasına bak

