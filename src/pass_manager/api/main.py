"""FastAPI ana uygulama."""

from __future__ import annotations

import json
from datetime import datetime, timezone, timedelta
from typing import Optional

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from .auth import hash_password, verify_password, create_token, verify_token
from .database import Database
from .models import (
    UserCreate,
    UserLogin,
    VaultEnvelopeRequest,
    VaultEnvelopeResponse,
)

app = FastAPI(
    title="Pass Manager API",
    description="Güvenli şifre yöneticisi REST API",
    version="1.0.0",
)

# CORS ayarları - iOS uygulaması için gerekli
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production'da spesifik domain'ler belirtilmeli
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()
db = Database()

GEORGIA_TZ = timezone(timedelta(hours=4), name="UTC+4")


def _utcnow() -> str:
    return datetime.now(GEORGIA_TZ).replace(microsecond=0).isoformat()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """JWT token'dan kullanıcı adını al."""
    token = credentials.credentials
    username = verify_token(token)
    if not username:
        raise HTTPException(status_code=401, detail="Geçersiz veya süresi dolmuş token")
    return username


def get_user_id(username: str) -> Optional[int]:
    """Kullanıcı ID'sini al."""
    with db.connection() as conn:
        cursor = conn.execute("SELECT id FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        return row["id"] if row else None


@app.post("/api/v1/auth/register")
async def register(user_data: UserCreate):
    """Yeni kullanıcı kaydı."""
    if len(user_data.username) < 3:
        raise HTTPException(status_code=400, detail="Kullanıcı adı en az 3 karakter olmalı")
    if len(user_data.password) < 8:
        raise HTTPException(status_code=400, detail="Parola en az 8 karakter olmalı")

    with db.connection() as conn:
        # Kullanıcı zaten var mı kontrol et
        cursor = conn.execute("SELECT id FROM users WHERE username = ?", (user_data.username,))
        if cursor.fetchone():
            raise HTTPException(status_code=409, detail="Kullanıcı adı zaten kullanılıyor")

        # Yeni kullanıcı oluştur
        password_hash = hash_password(user_data.password)
        now = _utcnow()
        conn.execute(
            "INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)",
            (user_data.username, password_hash, now),
        )
        conn.commit()

    token = create_token(user_data.username)
    return {"token": token, "username": user_data.username}


@app.post("/api/v1/auth/login")
async def login(user_data: UserLogin):
    """Kullanıcı girişi."""
    with db.connection() as conn:
        cursor = conn.execute(
            "SELECT id, password_hash FROM users WHERE username = ?",
            (user_data.username,),
        )
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=401, detail="Kullanıcı adı veya parola hatalı")

        if not verify_password(user_data.password, row["password_hash"]):
            raise HTTPException(status_code=401, detail="Kullanıcı adı veya parola hatalı")

        # Son giriş zamanını güncelle
        conn.execute(
            "UPDATE users SET last_login = ? WHERE id = ?",
            (_utcnow(), row["id"]),
        )
        conn.commit()

    token = create_token(user_data.username)
    return {"token": token, "username": user_data.username}


@app.get("/api/v1/vault")
async def get_vault(username: str = Depends(get_current_user)):
    """Kullanıcının vault'unu al."""
    user_id = get_user_id(username)
    if not user_id:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")

    with db.connection() as conn:
        cursor = conn.execute(
            "SELECT encrypted_envelope, updated_at FROM vaults WHERE user_id = ?",
            (user_id,),
        )
        row = cursor.fetchone()
        if not row:
            # Vault yoksa boş envelope döndür
            return VaultEnvelopeResponse(
                encrypted_envelope={},
                updated_at=_utcnow(),
            )

        envelope = json.loads(row["encrypted_envelope"])
        return VaultEnvelopeResponse(
            encrypted_envelope=envelope,
            updated_at=row["updated_at"],
        )


@app.post("/api/v1/vault")
async def save_vault(
    vault_data: VaultEnvelopeRequest,
    username: str = Depends(get_current_user),
):
    """Vault'u kaydet veya güncelle."""
    user_id = get_user_id(username)
    if not user_id:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")

    now = _utcnow()
    envelope_json = json.dumps(vault_data.encrypted_envelope)

    with db.connection() as conn:
        # Vault var mı kontrol et
        cursor = conn.execute("SELECT id FROM vaults WHERE user_id = ?", (user_id,))
        existing = cursor.fetchone()

        if existing:
            # Güncelle
            conn.execute(
                "UPDATE vaults SET encrypted_envelope = ?, updated_at = ? WHERE user_id = ?",
                (envelope_json, now, user_id),
            )
        else:
            # Yeni oluştur
            conn.execute(
                "INSERT INTO vaults (user_id, encrypted_envelope, created_at, updated_at) VALUES (?, ?, ?, ?)",
                (user_id, envelope_json, now, now),
            )
        conn.commit()

    return {"message": "Vault başarıyla kaydedildi", "updated_at": now}


@app.get("/api/v1/health")
async def health_check():
    """Sunucu sağlık kontrolü."""
    return {"status": "ok", "service": "pass-manager-api"}


# Web uygulamasını serve et
# Path: proje_root/web_app
web_app_path = Path(__file__).parent.parent.parent.parent / "web_app"
if web_app_path.exists():
    # Static dosyalar için (CSS, JS, vs.)
    static_files = StaticFiles(directory=str(web_app_path))
    app.mount("/static", static_files, name="static")
    
    @app.get("/")
    async def serve_index():
        """Ana sayfa - web uygulaması."""
        index_file = web_app_path / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file), media_type="text/html")
        return {"message": "Web uygulaması bulunamadı"}
    
    # Web uygulaması dosyalarını serve et (JS, CSS, vs.)
    @app.get("/{filename}")
    async def serve_web_files(filename: str):
        """Web uygulaması dosyalarını serve et."""
        # API endpoint'lerini atla
        if filename.startswith("api/"):
            raise HTTPException(status_code=404)
        
        file_path = web_app_path / filename
        if file_path.exists() and file_path.is_file() and file_path.suffix in [".js", ".css", ".html", ".json", ".png", ".jpg", ".ico"]:
            media_type = "text/javascript" if filename.endswith(".js") else \
                        "text/css" if filename.endswith(".css") else \
                        "text/html" if filename.endswith(".html") else \
                        "application/json" if filename.endswith(".json") else None
            return FileResponse(str(file_path), media_type=media_type)
        
        # Eğer dosya yoksa index.html'e yönlendir (SPA için)
        index_file = web_app_path / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file), media_type="text/html")
        raise HTTPException(status_code=404, detail="Dosya bulunamadı")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

