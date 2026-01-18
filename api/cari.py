"""
Cari (Customer Account) API endpoints
"""
from fastapi import APIRouter, HTTPException
from typing import Optional
from models import CariCreate, CariUpdate
from db_instance import db

router = APIRouter(prefix="/api/cari", tags=["cari"])


@router.get("")
async def cari_listele(arama: Optional[str] = "", tip: Optional[str] = ""):
    """List all customer accounts with optional search and filter"""
    try:
        cariler = db.cari_listele(arama, tip)
        return {"success": True, "data": cariler, "count": len(cariler)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{cari_id}")
async def cari_getir(cari_id: int):
    """Get a specific customer account by ID"""
    try:
        cari = db.cari_getir(cari_id)
        if not cari:
            raise HTTPException(status_code=404, detail="Cari hesap bulunamadı")
        return {"success": True, "data": cari}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("")
async def cari_ekle(cari: CariCreate):
    """Create a new customer account"""
    try:
        if not cari.unvan:
            raise HTTPException(status_code=400, detail="Ünvan zorunludur")
        
        result = db.cari_ekle(
            cari.cari_kodu, cari.unvan, cari.tip, cari.telefon, cari.email,
            cari.adres, cari.tc_kimlik_no, cari.vergi_no, cari.vergi_dairesi,
            cari.bakiye, cari.aciklama, cari.firma_tipi
        )
        
        if result:
            return {"success": True, "message": "Cari hesap başarıyla eklendi"}
        else:
            raise HTTPException(status_code=400, detail="Cari kodu zaten kullanılıyor")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{cari_id}")
async def cari_guncelle(cari_id: int, cari: CariUpdate):
    """Update a customer account"""
    try:
        if not cari.unvan:
            raise HTTPException(status_code=400, detail="Ünvan zorunludur")
        
        result = db.cari_guncelle(
            cari_id, cari.cari_kodu, cari.unvan, cari.tip, cari.telefon,
            cari.email, cari.adres, cari.vergi_no, cari.vergi_dairesi,
            cari.bakiye, cari.aciklama, cari.firma_tipi
        )
        
        if result:
            return {"success": True, "message": "Cari hesap başarıyla güncellendi"}
        else:
            raise HTTPException(status_code=400, detail="Güncelleme başarısız")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{cari_id}")
async def cari_sil(cari_id: int):
    """Delete a customer account"""
    try:
        result = db.cari_sil(cari_id)
        if result:
            return {"success": True, "message": "Cari hesap başarıyla silindi"}
        else:
            raise HTTPException(status_code=400, detail="Silme işlemi başarısız")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ara/tc")
async def cari_tc_ile_ara(tc_kimlik_no: str):
    """Search customer account by TC identity number"""
    try:
        cari = db.cari_tc_ile_ara(tc_kimlik_no)
        if not cari:
            raise HTTPException(status_code=404, detail="Cari hesap bulunamadı")
        return {"success": True, "data": cari}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ara/unvan")
async def cari_unvan_ile_ara(unvan: str):
    """Search customer account by title"""
    try:
        cari = db.cari_unvan_ile_ara(unvan)
        if not cari:
            raise HTTPException(status_code=404, detail="Cari hesap bulunamadı")
        return {"success": True, "data": cari}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sonraki-kod")
async def cari_sonraki_kod():
    """Get next available customer code"""
    try:
        kod = db.cari_sonraki_kod_olustur()
        return {"success": True, "data": {"cari_kodu": kod}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ekle-tc-kontrolu-ile")
async def cari_ekle_tc_kontrolu_ile(cari: CariCreate):
    """Create customer account with TC identity number check"""
    try:
        if not cari.unvan:
            raise HTTPException(status_code=400, detail="Ünvan zorunludur")
        
        basarili, mesaj = db.cari_ekle_tc_kontrolu_ile(
            cari.cari_kodu, cari.unvan, cari.tip, cari.telefon, cari.email,
            cari.adres, cari.tc_kimlik_no, cari.vergi_no, cari.vergi_dairesi,
            cari.bakiye, cari.aciklama, cari.firma_tipi
        )
        
        return {"success": basarili, "message": mesaj}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
