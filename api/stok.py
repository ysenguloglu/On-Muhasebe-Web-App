"""
Stok (Stock) API endpoints
"""
from fastapi import APIRouter, HTTPException
from typing import Optional
from models import (
    StokCreate, StokUpdate, StokMiktarAzalt, StokMiktarAzaltBatch
)
from db_instance import db

router = APIRouter(prefix="/api/stok", tags=["stok"])


@router.get("")
async def stok_listele(arama: Optional[str] = ""):
    """List all stock items with optional search"""
    try:
        urunler = db.stok_listele(arama)
        return {"success": True, "data": urunler, "count": len(urunler)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{stok_id}")
async def stok_getir(stok_id: int):
    """Get a specific stock item by ID"""
    try:
        urun = db.stok_getir(stok_id)
        if not urun:
            raise HTTPException(status_code=404, detail="Ürün bulunamadı")
        return {"success": True, "data": urun}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("")
async def stok_ekle(stok: StokCreate):
    """Create a new stock item"""
    try:
        if not stok.urun_adi:
            raise HTTPException(status_code=400, detail="Ürün adı zorunludur")
        result = db.stok_ekle(
            stok.urun_kodu, stok.urun_adi, stok.marka, stok.birim,
            stok.stok_miktari, stok.birim_fiyat, stok.aciklama
        )
        
        if result:
            return {"success": True, "message": "Ürün başarıyla eklendi"}
        else:
            raise HTTPException(status_code=400, detail="Ürün kodu zaten kullanılıyor")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{stok_id}")
async def stok_guncelle(stok_id: int, stok: StokUpdate):
    """Update a stock item"""
    try:
        if not stok.urun_adi:
            raise HTTPException(status_code=400, detail="Ürün adı zorunludur")
        result = db.stok_guncelle(
            stok_id, stok.urun_kodu, stok.urun_adi, stok.marka, stok.birim,
            stok.stok_miktari, stok.birim_fiyat, stok.aciklama
        )
        
        if result:
            return {"success": True, "message": "Ürün başarıyla güncellendi"}
        else:
            raise HTTPException(status_code=400, detail="Güncelleme başarısız")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{stok_id}")
async def stok_sil(stok_id: int):
    """Delete a stock item"""
    try:
        result = db.stok_sil(stok_id)
        if result:
            return {"success": True, "message": "Ürün başarıyla silindi"}
        else:
            raise HTTPException(status_code=400, detail="Silme işlemi başarısız")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ara/urun-adi")
async def stok_urun_adi_ile_ara(urun_adi: str):
    """Search stock by product name"""
    try:
        urun = db.stok_urun_adi_ile_ara(urun_adi)
        if not urun:
            raise HTTPException(status_code=404, detail="Ürün bulunamadı")
        return {"success": True, "data": urun}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ara/urun-kodu")
async def stok_urun_kodu_ile_ara(urun_kodu: str):
    """Search stock by product code"""
    try:
        urun = db.stok_urun_kodu_ile_ara(urun_kodu)
        if not urun:
            raise HTTPException(status_code=404, detail="Ürün bulunamadı")
        return {"success": True, "data": urun}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/miktar-azalt")
async def stok_miktar_azalt(request: StokMiktarAzalt):
    """Reduce stock quantity by product code"""
    try:
        basarili, mesaj = db.stok_miktar_azalt(request.urun_kodu, request.miktar)
        if basarili:
            return {"success": True, "message": mesaj}
        else:
            raise HTTPException(status_code=400, detail=mesaj)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/miktar-azalt-batch")
async def stok_miktar_azalt_batch(request: StokMiktarAzaltBatch):
    """Reduce stock quantities for multiple products"""
    try:
        basarili_mesajlar, hata_mesajlari = db.stok_miktar_azalt_batch(request.urunler)
        return {
            "success": len(hata_mesajlari) == 0,
            "basarili_mesajlar": basarili_mesajlar,
            "hata_mesajlari": hata_mesajlari
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
