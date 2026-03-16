"""
Araç Yönetimi (Modül 2) API
Araç kartı, belge takibi, bakım geçmişi
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional

from models import AracCreate, AracUpdate, AracBelgeCreate, AracBakimCreate
from db_instance import db
from api.auth import get_current_user, require_can_read_arac, require_can_write_arac

router = APIRouter(
    prefix="/api/arac",
    tags=["arac"],
    dependencies=[Depends(get_current_user), Depends(require_can_read_arac)],
)


@router.get("")
async def arac_listele(
    arama: Optional[str] = "",
    durum: Optional[str] = None,
):
    """Araç listesi. arama: plaka/marka/model/şasi; durum: aktif, bakımda, pasif."""
    try:
        liste = db.arac_listele(arama=arama or "", durum=durum)
        return {"success": True, "data": liste, "count": len(liste)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/belgeler/suresi-dolacak")
async def belgeler_suresi_dolacak(
    gun: int = 30,
):
    """Belirtilen gün sayısı içinde süresi dolacak belgeleri listeler."""
    try:
        liste = db.belge_suresi_dolacak_listele(gun=gun)
        return {"success": True, "data": liste, "count": len(liste)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/belgeler/takip")
async def belgeler_takip(
    arac_plakasi: Optional[str] = None,
    belge_turu: Optional[str] = None,
):
    """Belge ve son tarih takibi: tüm belgeler bitiş tarihine göre (en yakın önce)."""
    try:
        liste = db.belge_takip_listele(arac_plakasi=arac_plakasi, belge_turu=belge_turu)
        return {"success": True, "data": liste, "count": len(liste)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{arac_id}")
async def arac_getir(arac_id: int):
    """Tek araç detayı."""
    try:
        arac = db.arac_getir(arac_id)
        if not arac:
            raise HTTPException(status_code=404, detail="Araç bulunamadı")
        return {"success": True, "data": arac}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{arac_id}/belgeler")
async def arac_belgeleri_listele(arac_id: int):
    """Aracın belgelerini listeler."""
    arac = db.arac_getir(arac_id)
    if not arac:
        raise HTTPException(status_code=404, detail="Araç bulunamadı")
    try:
        liste = db.belge_listele(arac_id)
        return {"success": True, "data": liste, "count": len(liste)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{arac_id}/bakim")
async def arac_bakim_listele(arac_id: int):
    """Aracın bakım geçmişini listeler."""
    arac = db.arac_getir(arac_id)
    if not arac:
        raise HTTPException(status_code=404, detail="Araç bulunamadı")
    try:
        liste = db.bakim_listele(arac_id)
        return {"success": True, "data": liste, "count": len(liste)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{arac_id}/bakim-uyarilari")
async def arac_bakim_uyarilari(arac_id: int):
    """Aracın bakım uyarılarını döndürür (yağ 15k km/6 ay, fren 25k km, lastik 80k km/3 yıl)."""
    arac = db.arac_getir(arac_id)
    if not arac:
        raise HTTPException(status_code=404, detail="Araç bulunamadı")
    try:
        uyarilar = db.bakim_uyarilari_hesapla(arac_id)
        return {"success": True, "data": uyarilar}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------- Yazma (require_can_write_arac) ----------

@router.post("", dependencies=[Depends(require_can_write_arac)])
async def arac_ekle(body: AracCreate):
    """Yeni araç ekler."""
    try:
        ok, msg = db.arac_ekle(
            arac_plakasi=body.arac_plakasi,
            arac_tipi=body.arac_tipi or "diğer",
            marka=body.marka or "",
            model=body.model or "",
            model_yili=body.model_yili,
            sasi_no=body.sasi_no or "",
            motor_no=body.motor_no or "",
            guncel_km=body.guncel_km or 0,
            alis_tarihi=body.alis_tarihi,
            alis_fiyati=body.alis_fiyati,
            durum=body.durum or "aktif",
        )
        if ok:
            return {"success": True, "message": msg}
        raise HTTPException(status_code=400, detail=msg)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{arac_id}", dependencies=[Depends(require_can_write_arac)])
async def arac_guncelle(arac_id: int, body: AracUpdate):
    """Araç bilgilerini günceller."""
    mevcut = db.arac_getir(arac_id)
    if not mevcut:
        raise HTTPException(status_code=404, detail="Araç bulunamadı")
    try:
        ok, msg = db.arac_guncelle(
            arac_id=arac_id,
            arac_plakasi=body.arac_plakasi,
            arac_tipi=body.arac_tipi or "diğer",
            marka=body.marka or "",
            model=body.model or "",
            model_yili=body.model_yili,
            sasi_no=body.sasi_no or "",
            motor_no=body.motor_no or "",
            guncel_km=body.guncel_km or 0,
            alis_tarihi=body.alis_tarihi,
            alis_fiyati=body.alis_fiyati,
            durum=body.durum or "aktif",
        )
        if ok:
            return {"success": True, "message": msg}
        raise HTTPException(status_code=400, detail=msg)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{arac_id}", dependencies=[Depends(require_can_write_arac)])
async def arac_sil(arac_id: int):
    """Aracı siler (belge ve bakım kayıtları cascade silinir)."""
    mevcut = db.arac_getir(arac_id)
    if not mevcut:
        raise HTTPException(status_code=404, detail="Araç bulunamadı")
    try:
        ok = db.arac_sil(arac_id)
        if ok:
            return {"success": True, "message": "Araç silindi"}
        raise HTTPException(status_code=500, detail="Silme işlemi başarısız")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{arac_id}/belgeler", dependencies=[Depends(require_can_write_arac)])
async def arac_belge_ekle(arac_id: int, body: AracBelgeCreate):
    """Araca belge ekler."""
    arac = db.arac_getir(arac_id)
    if not arac:
        raise HTTPException(status_code=404, detail="Araç bulunamadı")
    if not body.bitis_tarihi:
        raise HTTPException(status_code=400, detail="Bitiş tarihi zorunludur")
    try:
        ok, msg = db.belge_ekle(
            arac_id=arac_id,
            belge_turu=body.belge_turu,
            duzenlenme_tarihi=body.duzenlenme_tarihi,
            bitis_tarihi=body.bitis_tarihi,
            belge_dosya_path=body.belge_dosya_path,
        )
        if ok:
            return {"success": True, "message": msg}
        raise HTTPException(status_code=400, detail=msg)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{arac_id}/bakim", dependencies=[Depends(require_can_write_arac)])
async def arac_bakim_ekle(arac_id: int, body: AracBakimCreate):
    """Araca bakım kaydı ekler."""
    arac = db.arac_getir(arac_id)
    if not arac:
        raise HTTPException(status_code=404, detail="Araç bulunamadı")
    try:
        ok, msg = db.bakim_ekle(
            arac_id=arac_id,
            bakim_turu=body.bakim_turu,
            aciklama=body.aciklama or "",
            bakim_tarihi=body.bakim_tarihi or "",
            bakim_km=body.bakim_km,
            maliyet=body.maliyet,
        )
        if ok:
            return {"success": True, "message": msg}
        raise HTTPException(status_code=400, detail=msg)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
