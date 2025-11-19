# 🔧 GitHub "Rejected" Hatası Çözümü

## 🎯 Sorun: "rejected" veya "authentication failed" hatası

Bu hata genellikle yanlış kullanıcı adı/parola veya eski kaydedilmiş bilgilerden kaynaklanır.

---

## ✅ ÇÖZÜM 1: Git Credential Helper'ı Sıfırla

PowerShell veya CMD'de şu komutları çalıştır:

```bash
# 1. Kaydedilmiş GitHub bilgilerini sil
git credential-manager erase https://github.com

# VEYA (eğer yukarıdaki çalışmazsa)
git credential reject https://github.com
```

Sonra tekrar dene:
```bash
git push -u origin main
```

---

## ✅ ÇÖZÜM 2: Remote URL'i Kontrol Et

Remote URL'in doğru olduğundan emin ol:

```bash
# Mevcut remote'u kontrol et
git remote -v

# Eğer yanlışsa, sil ve tekrar ekle
git remote remove origin
git remote add origin https://github.com/KULLANICI_ADIN/REPO_ADI.git

# Tekrar dene
git push -u origin main
```

**⚠️ ÖNEMLİ:** `KULLANICI_ADIN` ve `REPO_ADI` kısımlarını kendi bilgilerinle değiştir!

---

## ✅ ÇÖZÜM 3: Personal Access Token Kullan

GitHub artık normal parola kabul etmiyor, **token** gerekli!

### Token Nasıl Alınır:

1. **GitHub'a git:** https://github.com
2. **Sağ üstteki profil fotoğrafına tıkla** → **"Settings"**
3. **Sol menüden "Developer settings"** seç
4. **"Personal access tokens"** → **"Tokens (classic)"**
5. **"Generate new token"** → **"Generate new token (classic)"**
6. **Note:** `pass-manager-deploy` yaz
7. **Expiration:** 90 days (veya istediğin süre)
8. **Scopes:** Aşağıdakileri işaretle:
   - ✅ `repo` (tüm alt seçenekler otomatik işaretlenir)
   - ✅ `workflow` (eğer varsa)
9. En altta **"Generate token"** butonuna tıkla
10. **Token'ı kopyala** (bir daha gösterilmez! Not defterine kaydet)

### Token'ı Kullan:

```bash
# Önce credential'ları temizle
git credential-manager erase https://github.com

# Tekrar push dene
git push -u origin main
```

**İstendiğinde:**
- **Username:** GitHub kullanıcı adın
- **Password:** Normal parolan DEĞİL, az önce kopyaladığın **TOKEN'ı** yapıştır

---

## ✅ ÇÖZÜM 4: URL'de Token Kullan (En Kolay)

Remote URL'e token'ı ekleyebilirsin:

```bash
# Önce remote'u sil
git remote remove origin

# Token'ı URL'e ekle (TOKEN kısmını kendi token'ınla değiştir)
git remote add origin https://TOKEN@github.com/KULLANICI_ADIN/REPO_ADI.git

# Artık push yaparken soru sormayacak
git push -u origin main
```

**Örnek:**
```bash
git remote add origin https://ghp_abc123xyz456@github.com/tanjiro123/pass-manager.git
```

**⚠️ DİKKAT:** Bu yöntem güvenli değil çünkü token URL'de görünür. Sadece test için kullan!

---

## ✅ ÇÖZÜM 5: SSH Kullan (En Güvenli - Opsiyonel)

SSH key kullanmak daha güvenli ama biraz daha karmaşık:

### SSH Key Oluştur:
```bash
# SSH key oluştur (e-posta adresini değiştir)
ssh-keygen -t ed25519 -C "senin@email.com"

# Enter'a bas (dosya adı için)
# Enter'a bas (parola için, boş bırakabilirsin)
```

### SSH Key'i GitHub'a Ekle:
1. Oluşturulan key'i kopyala:
```bash
cat ~/.ssh/id_ed25519.pub
```
2. GitHub → Settings → SSH and GPG keys → New SSH key
3. Key'i yapıştır ve kaydet

### Remote'u SSH'a Çevir:
```bash
git remote remove origin
git remote add origin git@github.com:KULLANICI_ADIN/REPO_ADI.git
git push -u origin main
```

---

## 🎯 Hangi Çözümü Kullanmalıyım?

1. **En Kolay:** ÇÖZÜM 3 (Personal Access Token)
2. **En Güvenli:** ÇÖZÜM 5 (SSH)
3. **Hızlı Test:** ÇÖZÜM 4 (URL'de token)

**Öneri:** ÇÖZÜM 3'ü kullan, en pratik!

---

## 🆘 "non-fast-forward" veya "Updates were rejected" Hatası

**📖 DETAYLI ÇÖZÜM:** `GITHUB_MERGE_COZUM.md` dosyasına bak!

**Hızlı çözüm:**
```bash
# GitHub'daki değişiklikleri al ve birleştir
git pull origin main --allow-unrelated-histories

# Sonra push yap
git push -u origin main
```

---

## 🆘 Hala Çalışmıyor mu?

### Kontrol Listesi:

- [ ] GitHub'da repository oluşturdun mu?
- [ ] Repository adı doğru mu?
- [ ] Kullanıcı adı doğru mu?
- [ ] Token'ı doğru kopyaladın mı? (başında/sonunda boşluk yok mu?)
- [ ] Token'da `repo` scope'u var mı?
- [ ] Token'ın süresi dolmadı mı?
- [ ] Remote URL doğru mu? (`git remote -v` ile kontrol et)

### Hata Mesajını Kontrol Et:

Tam hata mesajını paylaş, daha spesifik yardım edebilirim!

---

## 📝 Örnek Başarılı Çıktı

Eğer şunu görürsen başarılı:

```
Enumerating objects: 50, done.
Counting objects: 100% (50/50), done.
Delta compression using up to 8 threads
Compressing objects: 100% (45/45), done.
Writing objects: 100% (50/50), 15.23 KiB | 2.18 MiB/s, done.
Total 50 (delta 5), reused 0 (delta 0), pack-reused 0
remote: Resolving deltas: 100% (5/5), done.
To https://github.com/KULLANICI_ADIN/REPO_ADI.git
 * [new branch]      main -> main
Branch 'main' set up to track remote branch 'main' from 'origin'.
```

🎉 **Başarılı!** Artık Railway'a bağlayabilirsin!

