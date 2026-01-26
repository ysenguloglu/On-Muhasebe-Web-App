"""
İş Prosesi API endpoints
"""
from fastapi import APIRouter, HTTPException
from models import IsProsesiCreate, IsProsesiUpdate, IsProsesiMaddeCreate, IsProsesiMaddeUpdate
from db_instance import db

router = APIRouter(prefix="/api/is-prosesi", tags=["is-prosesi"])


@router.get("")
async def is_prosesi_listele():
    """List all work processes"""
    try:
        prosesler = db.is_prosesi_listele()
        # Her proses için maddeleri de getir
        for proses in prosesler:
            maddeler = db.is_prosesi_maddeleri_getir(proses['id'])
            proses['maddeler'] = maddeler
        return {"success": True, "data": prosesler, "count": len(prosesler)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{proses_id}")
async def is_prosesi_getir(proses_id: int):
    """Get a specific work process by ID"""
    try:
        proses = db.is_prosesi_getir(proses_id)
        if not proses:
            raise HTTPException(status_code=404, detail="İş prosesi bulunamadı")
        
        # Maddeleri de getir
        maddeler = db.is_prosesi_maddeleri_getir(proses_id)
        proses['maddeler'] = maddeler
        
        return {"success": True, "data": proses}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("")
async def is_prosesi_ekle(proses: IsProsesiCreate):
    """Create a new work process"""
    try:
        success, message, proses_id = db.is_prosesi_ekle(
            proses_adi=proses.proses_adi,
            aciklama=proses.aciklama or "",
            proses_tipi=proses.proses_tipi or None
        )
        
        if not success:
            raise HTTPException(status_code=400, detail=message)
        
        # Maddeleri ekle
        if proses.maddeler and proses_id:
            for madde in proses.maddeler:
                db.is_prosesi_madde_ekle(
                    proses_id=proses_id,
                    sira_no=madde.sira_no,
                    madde_adi=madde.madde_adi,
                    aciklama=madde.aciklama or "",
                    kullanilan_malzemeler=madde.kullanilan_malzemeler or ""
                )
        
        # Oluşturulan prosesi getir
        yeni_proses = db.is_prosesi_getir(proses_id)
        if yeni_proses:
            maddeler = db.is_prosesi_maddeleri_getir(proses_id)
            yeni_proses['maddeler'] = maddeler
        
        return {"success": True, "message": message, "data": yeni_proses}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{proses_id}")
async def is_prosesi_guncelle(proses_id: int, proses: IsProsesiUpdate):
    """Update a work process"""
    try:
        success, message = db.is_prosesi_guncelle(
            proses_id=proses_id,
            proses_adi=proses.proses_adi,
            aciklama=proses.aciklama or "",
            proses_tipi=proses.proses_tipi or None
        )
        
        if not success:
            raise HTTPException(status_code=400, detail=message)
        
        # Güncellenmiş prosesi getir
        guncellenmis_proses = db.is_prosesi_getir(proses_id)
        if guncellenmis_proses:
            maddeler = db.is_prosesi_maddeleri_getir(proses_id)
            guncellenmis_proses['maddeler'] = maddeler
        
        return {"success": True, "message": message, "data": guncellenmis_proses}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{proses_id}")
async def is_prosesi_sil(proses_id: int):
    """Delete a work process"""
    try:
        success, message = db.is_prosesi_sil(proses_id)
        
        if not success:
            raise HTTPException(status_code=400, detail=message)
        
        return {"success": True, "message": message}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== PROSES MADDELERİ ENDPOINT'LERİ ==========


@router.get("/{proses_id}/maddeler")
async def is_prosesi_maddeleri_getir(proses_id: int):
    """Get all items for a work process"""
    try:
        maddeler = db.is_prosesi_maddeleri_getir(proses_id)
        return {"success": True, "data": maddeler, "count": len(maddeler)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{proses_id}/maddeler")
async def is_prosesi_madde_ekle(proses_id: int, madde: IsProsesiMaddeCreate):
    """Add a new item to a work process"""
    try:
        success, message, madde_id = db.is_prosesi_madde_ekle(
            proses_id=proses_id,
            sira_no=madde.sira_no,
            madde_adi=madde.madde_adi,
            aciklama=madde.aciklama or "",
            kullanilan_malzemeler=madde.kullanilan_malzemeler or ""
        )
        
        if not success:
            raise HTTPException(status_code=400, detail=message)
        
        return {"success": True, "message": message, "data": {"id": madde_id}}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/maddeler/{madde_id}")
async def is_prosesi_madde_guncelle(madde_id: int, madde: IsProsesiMaddeUpdate):
    """Update a work process item"""
    try:
        success, message = db.is_prosesi_madde_guncelle(
            madde_id=madde_id,
            sira_no=madde.sira_no,
            madde_adi=madde.madde_adi,
            aciklama=madde.aciklama or "",
            kullanilan_malzemeler=madde.kullanilan_malzemeler or "",
            tamamlandi=madde.tamamlandi or False
        )
        
        if not success:
            raise HTTPException(status_code=400, detail=message)
        
        return {"success": True, "message": message}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/maddeler/{madde_id}")
async def is_prosesi_madde_sil(madde_id: int):
    """Delete a work process item"""
    try:
        success, message = db.is_prosesi_madde_sil(madde_id)
        
        if not success:
            raise HTTPException(status_code=400, detail=message)
        
        return {"success": True, "message": message}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/maddeler/{madde_id}/tamamla")
async def is_prosesi_madde_tamamla(madde_id: int, tamamlandi: bool = True):
    """Mark a work process item as completed or not"""
    try:
        success, message = db.is_prosesi_tamamla_madde(madde_id, tamamlandi)
        
        if not success:
            raise HTTPException(status_code=400, detail=message)
        
        return {"success": True, "message": message}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
