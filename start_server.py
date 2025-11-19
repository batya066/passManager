"""API sunucusunu başlatma scripti."""

import os
import uvicorn
from pass_manager.api.main import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    
    print("🚀 Pass Manager API sunucusu başlatılıyor...")
    print(f"📡 Sunucu: http://{host}:{port}")
    print(f"📚 API Dokümantasyonu: http://localhost:{port}/docs")
    print("\nÇıkmak için Ctrl+C basın.\n")
    uvicorn.run(app, host=host, port=port, log_level="info")

