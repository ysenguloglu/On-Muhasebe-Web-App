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
from api.auth import router as auth_router
from api.stok import router as stok_router
from api.cari import router as cari_router
from api.is_evraki import router as is_evraki_router
from api.is_prosesi import router as is_prosesi_router
from api.excel import router as excel_router
from api.aylik_rapor import router as aylik_rapor_router

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
        # Hiç kullanıcı yoksa varsayılan admin (admin / admin123) oluştur
        ok, msg = db.auth.seed_default_admin()
        if ok:
            print("✅ " + msg)
    except Exception as e:
        print(f"⚠️ Veritabanı başlatma hatası (uygulama devam ediyor): {e}")
        import traceback
        traceback.print_exc()
        # Hata olsa bile uygulama başlasın, belki tablolar zaten var

    # Aylık rapor otomatik gönderimi: AYLIK_RAPOR_OTOMATIK=1 veya true ise her ayın 1'i 09:00 (Türkiye)
    otomatik = str(os.getenv("AYLIK_RAPOR_OTOMATIK", "")).lower() in ("1", "true", "yes")
    if otomatik:
        try:
            from apscheduler.schedulers.asyncio import AsyncIOScheduler
            from api.aylik_rapor import aylik_rapor_cron_job
            s = AsyncIOScheduler()
            s.add_job(aylik_rapor_cron_job, "cron", day=1, hour=9, minute=0, timezone="Europe/Istanbul", id="aylik_rapor")
            s.start()
            app.state.scheduler = s
            print("✅ Aylık rapor otomatik gönderim: her ayın 1'i 09:00 (İstanbul) olarak ayarlandı.")
        except Exception as e:
            print(f"⚠️ Aylık rapor otomatik gönderim başlatılamadı: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Kapanırken zamanlayıcıyı durdur"""
    s = getattr(app.state, "scheduler", None)
    if s is not None:
        try:
            s.shutdown(wait=False)
        except Exception:
            pass

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

# Include routers (auth login herkese açık, diğer API'ler token ister)
app.include_router(auth_router)
app.include_router(routes_router)
app.include_router(excel_router)
app.include_router(stok_router)
app.include_router(cari_router)
app.include_router(is_evraki_router)
app.include_router(is_prosesi_router)
app.include_router(aylik_rapor_router)


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
