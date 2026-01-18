"""
FastAPI web service for Ön Muhasebe application
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
import sys

from db_instance import db
from routes import router as routes_router
from api.stok import router as stok_router
from api.cari import router as cari_router
from api.is_evraki import router as is_evraki_router
from api.excel import router as excel_router

app = FastAPI(
    title="Ön Muhasebe API",
    description="Stok, Cari Hesap ve İş Evrakı Yönetimi API",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    """Uygulama başlarken veritabanı tablolarını kontrol et"""
    try:
        print("🔄 Veritabanı tabloları kontrol ediliyor...")
        db.db_conn.init_database()
        print("✅ Veritabanı hazır!")
    except Exception as e:
        print(f"⚠️ Veritabanı başlatma hatası (uygulama devam ediyor): {e}")
        import traceback
        traceback.print_exc()
        # Hata olsa bile uygulama başlasın, belki tablolar zaten var

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files için klasör oluştur
static_dir = "static"
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Include routers
# Excel router'ı stok router'ından önce include et (daha spesifik route'lar önce)
app.include_router(routes_router)
app.include_router(excel_router)
app.include_router(stok_router)
app.include_router(cari_router)
app.include_router(is_evraki_router)


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
