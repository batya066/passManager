# Pass Manager Web Uygulaması

Bu web uygulaması iOS, Android ve bilgisayardan erişilebilir. Tüm encryption client-side yapılır.

## Özellikler

- ✅ **Client-Side Encryption:** Tüm veriler tarayıcıda şifrelenir
- ✅ **Responsive Design:** Mobil ve masaüstü uyumlu
- ✅ **PWA Desteği:** Ana ekrana eklenebilir
- ✅ **Offline Çalışma:** (Yakında)
- ✅ **Güvenli:** Master password sunucuya gönderilmez

## Kurulum

### 1. Statik Dosya Sunucusu

Web uygulamasını herhangi bir statik dosya sunucusunda barındırabilirsiniz:

#### Python ile:
```bash
cd web_app
python -m http.server 8080
```

#### Node.js ile:
```bash
cd web_app
npx serve
```

#### Nginx ile:
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    root /path/to/web_app;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

### 2. API Sunucusunu Başlat

API sunucusu ayrı bir portta çalışmalı (örn: 8000).

### 3. CORS Ayarları

API sunucusunda CORS ayarlarını web uygulamasının domain'ini içerecek şekilde güncelleyin:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-web-app-domain.com", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Kullanım

1. Web uygulamasını açın
2. API URL'ini girin (örn: `https://your-api.railway.app`)
3. Giriş yapın veya kayıt olun
4. Ana parolanızı girin
5. Vault'unuzu kullanmaya başlayın!

## Güvenlik

- Tüm encryption tarayıcıda yapılır (Web Crypto API)
- Master password hiçbir zaman sunucuya gönderilmez
- Token localStorage'da saklanır (production'da daha güvenli bir yöntem kullanılabilir)

## Notlar

- Web Crypto API modern tarayıcılarda çalışır
- HTTPS kullanmanız önerilir
- iOS Safari'de test edin

