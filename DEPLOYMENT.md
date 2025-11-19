# 🚀 Ücretsiz Sunucu Deployment Kılavuzu

## En İyi Ücretsiz Seçenekler

### 1. **Railway.app** ⭐ (ÖNERİLEN)
- **Ücretsiz Tier:** $5 kredi/ay (yeterli)
- **Kurulum:** Çok kolay, GitHub ile otomatik deploy
- **URL:** https://railway.app
- **Avantajlar:**
  - Otomatik HTTPS
  - GitHub entegrasyonu
  - Kolay kurulum
  - PostgreSQL desteği (ücretsiz)

**Kurulum:**
1. Railway.app'e GitHub ile giriş yap
2. "New Project" > "Deploy from GitHub repo"
3. Reponu seç
4. Otomatik olarak deploy edilir!

### 2. **Render.com**
- **Ücretsiz Tier:** 750 saat/ay (yeterli)
- **URL:** https://render.com
- **Avantajlar:**
  - Otomatik HTTPS
  - Kolay kurulum
  - PostgreSQL ücretsiz

**Kurulum:**
1. Render.com'a kayıt ol
2. "New Web Service" seç
3. GitHub reponu bağla
4. Build command: `pip install -r requirements.txt`
5. Start command: `python start_server.py`

### 3. **Fly.io**
- **Ücretsiz Tier:** 3 shared-cpu-1x VM
- **URL:** https://fly.io
- **Avantajlar:**
  - Global edge network
  - Çok hızlı
  - PostgreSQL desteği

### 4. **PythonAnywhere**
- **Ücretsiz Tier:** Sınırlı ama yeterli
- **URL:** https://www.pythonanywhere.com
- **Avantajlar:**
  - Python odaklı
  - Kolay kurulum
  - Ücretsiz SSL

## Railway.app ile Hızlı Kurulum

### Adım 1: Railway'a Giriş
```bash
# Railway CLI kurulumu (opsiyonel)
npm i -g @railway/cli
railway login
```

### Adım 2: Projeyi Deploy Et
1. Railway.app'e git
2. "New Project" > "Deploy from GitHub"
3. Reponu seç
4. Otomatik olarak deploy edilir!

### Adım 3: Environment Variables
Railway dashboard'da şu değişkenleri ekle:
```
JWT_SECRET=your_secret_key_here
PORT=8000
```

### Adım 4: Domain Ayarla
Railway otomatik olarak bir domain verir: `your-app.railway.app`

## Render.com ile Kurulum

### 1. Render Dashboard
1. https://render.com'a git
2. "New +" > "Web Service"
3. GitHub reponu bağla

### 2. Ayarlar
- **Name:** pass-manager-api
- **Environment:** Python 3
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `python start_server.py`
- **Plan:** Free

### 3. Environment Variables
```
JWT_SECRET=your_secret_key_here
```

## Production İçin Önemli Ayarlar

### 1. start_server.py Güncelle
```python
import os
import uvicorn
from pass_manager.api.main import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    uvicorn.run(app, host=host, port=port)
```

### 2. CORS Ayarları
Production'da CORS'u sınırla:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-web-app-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 3. JWT Secret
Environment variable'dan al:
```python
JWT_SECRET = os.environ.get("JWT_SECRET", secrets.token_urlsafe(32))
```

## Veritabanı (Opsiyonel)

### Railway PostgreSQL
1. Railway dashboard'da "New" > "Database" > "PostgreSQL"
2. Otomatik olarak bağlanır

### Render PostgreSQL
1. "New +" > "PostgreSQL"
2. Free plan seç
3. Connection string'i environment variable olarak ekle

## Test Etme

Deploy sonrası:
```bash
curl https://your-app.railway.app/api/v1/health
```

Başarılı yanıt:
```json
{"status": "ok", "service": "pass-manager-api"}
```

## Notlar

- Railway ve Render otomatik HTTPS sağlar
- Ücretsiz tier'lar genellikle yeterlidir
- Uyku modu olabilir (ilk istekte yavaş açılır)
- Production için paid plan düşünebilirsin

