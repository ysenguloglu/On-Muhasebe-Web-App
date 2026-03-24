"""
Şoför Yönetimi API
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional

from models import SoforCreate, SoforUpdate
from db_instance import db
from api.auth import get_current_user, require_can_write_module, require_not_sofor

router = APIRouter(prefix="/api/sofor", tags=["sofor"], dependencies=[Depends(get_current_user), Depends(require_not_sofor)])


@router.get("")
async def sofor_listele(arama: Optional[str] = "", durum: Optional[str] = None):
    """Şoför listesi (arama: ad, TC, telefon, SRC no; durum filtresi)."""
    try:
        liste = db.sofor_listele(arama=arama or "", durum=durum)
        return {"success": True, "data": liste, "count": len(liste)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{sofor_id}")
async def sofor_getir(sofor_id: int):
    """Tek şoför detayı."""
    try:
        row = db.sofor_getir(sofor_id)
        if not row:
            raise HTTPException(status_code=404, detail="Şoför bulunamadı")
        return {"success": True, "data": row}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("", dependencies=[Depends(require_can_write_module("sofor"))])
async def sofor_ekle(body: SoforCreate):
    """Yeni şoför ekler (yalnızca admin)."""
    try:
        ok, msg = db.sofor_ekle(
            ad_soyad=body.ad_soyad,
            tc_kimlik_no=body.tc_kimlik_no,
            telefon=body.telefon,
            email=body.email,
            adres=body.adres,
            ise_baslama_tarihi=body.ise_baslama_tarihi,
            src_belge_no=body.src_belge_no,
            src_bitis_tarihi=body.src_bitis_tarihi,
            ehliyet_sinifi=body.ehliyet_sinifi,
            ehliyet_bitis_tarihi=body.ehliyet_bitis_tarihi,
            psikoteknik_bitis=body.psikoteknik_bitis,
            acil_iletisim=body.acil_iletisim,
            iban=body.iban,
            durum=body.durum or "aktif",
        )
        if ok:
            return {"success": True, "message": msg}
        raise HTTPException(status_code=400, detail=msg)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{sofor_id}", dependencies=[Depends(require_can_write_module("sofor"))])
async def sofor_guncelle(sofor_id: int, body: SoforUpdate):
    """Şoför günceller (yalnızca admin)."""
    mevcut = db.sofor_getir(sofor_id)
    if not mevcut:
        raise HTTPException(status_code=404, detail="Şoför bulunamadı")
    try:
        ok, msg = db.sofor_guncelle(
            sofor_id=sofor_id,
            ad_soyad=body.ad_soyad,
            tc_kimlik_no=body.tc_kimlik_no,
            telefon=body.telefon,
            email=body.email,
            adres=body.adres,
            ise_baslama_tarihi=body.ise_baslama_tarihi,
            src_belge_no=body.src_belge_no,
            src_bitis_tarihi=body.src_bitis_tarihi,
            ehliyet_sinifi=body.ehliyet_sinifi,
            ehliyet_bitis_tarihi=body.ehliyet_bitis_tarihi,
            psikoteknik_bitis=body.psikoteknik_bitis,
            acil_iletisim=body.acil_iletisim,
            iban=body.iban,
            durum=body.durum or "aktif",
        )
        if ok:
            return {"success": True, "message": msg}
        raise HTTPException(status_code=400, detail=msg)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{sofor_id}", dependencies=[Depends(require_can_write_module("sofor"))])
async def sofor_sil(sofor_id: int):
    """Şoför siler (yalnızca admin)."""
    mevcut = db.sofor_getir(sofor_id)
    if not mevcut:
        raise HTTPException(status_code=404, detail="Şoför bulunamadı")
    try:
        ok = db.sofor_sil(sofor_id)
        if ok:
            return {"success": True, "message": "Şoför silindi"}
        raise HTTPException(status_code=500, detail="Silme işlemi başarısız")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
