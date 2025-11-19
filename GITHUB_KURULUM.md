# 📦 GitHub'a Proje Yükleme - Adım Adım

## 🎯 ADIM 1: GitHub'da Repository Oluştur

1. **GitHub'a git:** https://github.com
2. **Giriş yap** (hesabın yoksa kayıt ol)
3. Sağ üstteki **"+"** butonuna tıkla → **"New repository"**
4. Repository adını gir (örn: `pass-manager`)
5. **"Public"** veya **"Private"** seç (senin tercihin)
6. **"Add a README file"** işaretleme (boş bırak)
7. **"Create repository"** butonuna tıkla

---

## 🎯 ADIM 2: Git Kurulu mu Kontrol Et

Windows'ta PowerShell veya CMD aç ve şunu yaz:

```bash
git --version
```

Eğer "git is not recognized" hatası alırsan:

1. **Git'i indir:** https://git-scm.com/download/win
2. İndirilen dosyayı çalıştır
3. Tüm ayarları varsayılan bırak, "Next" diye diye kur
4. Bilgisayarı yeniden başlat

---

## 🎯 ADIM 3: Projeyi GitHub'a Yükle

### PowerShell veya CMD'de şu komutları sırayla çalıştır:

```bash
# 1. Proje klasörüne git
cd C:\Users\Tanjiro\Documents\CODEX\passManager

# 2. Git'i başlat (eğer daha önce yapmadıysan)
git init

# 3. Tüm dosyaları ekle
git add .

# 4. İlk commit'i yap
git commit -m "Initial commit - Pass Manager projesi"

# 5. Ana branch'i ayarla
git branch -M main

# 6. GitHub repository'yi bağla
# NOT: KULLANICI_ADIN ve REPO_ADI kısımlarını kendi bilgilerinle değiştir!
git remote add origin https://github.com/KULLANICI_ADIN/REPO_ADI.git

# 7. GitHub'a yükle
git push -u origin main
```

### ⚠️ ÖNEMLİ: 6. adımda kendi bilgilerini kullan!

**Örnek:**
- GitHub kullanıcı adın: `tanjiro123`
- Repository adın: `pass-manager`
- O zaman komut şöyle olur:
```bash
git remote add origin https://github.com/tanjiro123/pass-manager.git
```

---

## 🎯 ADIM 4: GitHub Giriş Bilgileri İste

7. adımda (`git push`) GitHub kullanıcı adı ve parola isteyecek:

1. **Kullanıcı adını gir**
2. **Parola gir** (normal parolan değil, **Personal Access Token** gerekli!)

### Personal Access Token Nasıl Alınır?

1. GitHub'da sağ üstteki profil fotoğrafına tıkla
2. **"Settings"** seç
3. Sol menüden **"Developer settings"** seç
4. **"Personal access tokens"** → **"Tokens (classic)"**
5. **"Generate new token"** → **"Generate new token (classic)"**
6. **Note:** `railway-deploy` yaz
7. **Expiration:** 90 days (veya istediğin süre)
8. **Scopes:** `repo` işaretle (tüm alt seçenekler otomatik işaretlenir)
9. En altta **"Generate token"** butonuna tıkla
10. **Token'ı kopyala** (bir daha gösterilmez!)
11. `git push` komutunda parola yerine bu token'ı kullan

---

## ✅ Başarılı Oldu mu?

Eğer şöyle bir mesaj görürsen başarılı:

```
Enumerating objects: X, done.
Counting objects: 100% (X/X), done.
Writing objects: 100% (X/X), done.
To https://github.com/KULLANICI_ADIN/REPO_ADI.git
 * [new branch]      main -> main
```

GitHub'da repository'ne git, dosyaların orada olduğunu gör!

---

## 🆘 Sorun mu Var?

### "fatal: not a git repository"
```bash
git init
```
komutunu çalıştırdın mı? Çalıştır.

### "remote origin already exists"
```bash
git remote remove origin
git remote add origin https://github.com/KULLANICI_ADIN/REPO_ADI.git
```

### "Authentication failed"
- Personal Access Token kullandın mı?
- Token'ı doğru kopyaladın mı?
- `repo` scope'u var mı?

### "Permission denied"
- GitHub'da repository'yi oluşturdun mu?
- Repository adı doğru mu?
- Kullanıcı adı doğru mu?

---

## 🎉 Sonraki Adım

GitHub'a yükledikten sonra:

1. Railway.app'e git
2. "New Project" → "Deploy from GitHub repo"
3. Repository'ni seç
4. Otomatik deploy başlar!

**`RAILWAY_KURULUM.md` dosyasına bak!**

