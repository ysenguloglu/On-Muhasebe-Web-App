"""
İş Evrakı (Work Order) API endpoints
"""
from fastapi import APIRouter, HTTPException
import json
from models import IsEvrakiCreate, IsEvrakiCreateWithEmail
from api.pdf_email import pdf_olustur_api, email_gonder_api
from db_instance import db

router = APIRouter(prefix="/api/is-evraki", tags=["is-evraki"])


@router.get("")
async def is_evraki_listele():
    """List all work orders"""
    try:
        evraklar = db.is_evraki_listele()
        return {"success": True, "data": evraklar, "count": len(evraklar)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("")
async def is_evraki_ekle(evrak: IsEvrakiCreate):
    """Create a new work order"""
    try:
        if not evrak.musteri_unvan:
            raise HTTPException(status_code=400, detail="Müşteri ünvanı zorunludur")
        
        basarili, mesaj = db.is_evraki_ekle(
            evrak.is_emri_no, evrak.tarih, evrak.musteri_unvan, evrak.telefon,
            evrak.arac_plakasi, evrak.cekici_dorse, evrak.marka_model,
            evrak.talep_edilen_isler, evrak.musteri_sikayeti, evrak.yapilan_is,
            evrak.baslama_saati, evrak.bitis_saati, evrak.kullanilan_urunler,
            evrak.toplam_tutar, evrak.tc_kimlik_no
        )
        
        if basarili:
            return {"success": True, "message": mesaj}
        else:
            raise HTTPException(status_code=400, detail=mesaj)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/kaydet-ve-gonder")
async def is_evraki_kaydet_ve_gonder(evrak: IsEvrakiCreateWithEmail):
    """İş evrakını kaydet, PDF oluştur ve e-posta gönder"""
    import os
    
    try:
        if not evrak.musteri_unvan:
            raise HTTPException(status_code=400, detail="Müşteri ünvanı zorunludur")
        
        # Kullanılan ürünleri parse et
        urunler = []
        if evrak.kullanilan_urunler:
            try:
                urunler = json.loads(evrak.kullanilan_urunler)
            except:
                pass
        
        # Stok miktarlarını azalt
        stok_urunler_listesi = []
        for urun in urunler:
            urun_kodu = urun.get("urun_kodu", "").strip()
            if urun_kodu:
                stok_urunler_listesi.append({
                    "urun_kodu": urun_kodu,
                    "miktar": urun.get("adet", 0),
                    "urun_adi": urun.get("urun_adi", "")
                })
        
        stok_mesajlari = {"basarili": [], "hatali": []}
        if stok_urunler_listesi:
            basarili_mesajlar, hata_mesajlari = db.stok_miktar_azalt_batch(stok_urunler_listesi)
            stok_mesajlari["basarili"] = basarili_mesajlar
            stok_mesajlari["hatali"] = hata_mesajlari
        
        # Cari hesabı ekle (TC kontrolü ile)
        cari_mesaji = ""
        if evrak.musteri_unvan:
            vergi_no_deger = evrak.tc_kimlik_no if evrak.tc_kimlik_no else ""
            basarili, mesaj = db.cari_ekle_tc_kontrolu_ile(
                cari_kodu="",
                unvan=evrak.musteri_unvan,
                tip="Müşteri",
                telefon=evrak.telefon,
                email=evrak.musteri_email,
                adres=evrak.musteri_adres,
                tc_kimlik_no=evrak.tc_kimlik_no if evrak.tc_kimlik_no else "",
                vergi_no=vergi_no_deger,
                vergi_dairesi=evrak.vergi_dairesi,
                bakiye=0,
                aciklama="İş evrakından otomatik eklendi",
                firma_tipi=evrak.firma_tipi
            )
            cari_mesaji = mesaj
        
        # İş evrakını veritabanına kaydet
        basarili, hata_mesaji = db.is_evraki_ekle(
            evrak.is_emri_no, evrak.tarih, evrak.musteri_unvan, evrak.telefon,
            evrak.arac_plakasi, evrak.cekici_dorse, evrak.marka_model,
            evrak.talep_edilen_isler, evrak.musteri_sikayeti, evrak.yapilan_is,
            evrak.baslama_saati, evrak.bitis_saati, evrak.kullanilan_urunler,
            evrak.toplam_tutar, evrak.tc_kimlik_no
        )
        
        if not basarili:
            raise HTTPException(status_code=400, detail=f"İş evrakı kaydedilemedi: {hata_mesaji}")
        
        # PDF oluştur ve e-posta gönder
        pdf_path = None
        email_sent = False
        
        if evrak.send_email:
            try:
                pdf_path = await pdf_olustur_api(evrak, urunler)
                if pdf_path:
                    email_sent = await email_gonder_api(evrak, pdf_path)
                    # PDF dosyasını temizle (geçici dosya)
                    try:
                        if os.path.exists(pdf_path):
                            os.remove(pdf_path)
                    except:
                        pass
            except Exception as e:
                # PDF/Email hatası olsa bile kayıt başarılı
                return {
                    "success": True,
                    "message": "İş evrakı kaydedildi ancak PDF/e-posta gönderiminde hata oluştu",
                    "warning": str(e),
                    "stok_mesajlari": stok_mesajlari,
                    "cari_mesaji": cari_mesaji
                }
        
        return {
            "success": True,
            "message": "İş evrakı başarıyla kaydedildi" + (" ve e-posta gönderildi" if email_sent else ""),
            "stok_mesajlari": stok_mesajlari,
            "cari_mesaji": cari_mesaji,
            "email_sent": email_sent
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sonraki-no")
async def is_emri_no_sonraki():
    """Get next available work order number"""
    try:
        no = db.is_emri_no_sonraki()
        return {"success": True, "data": {"is_emri_no": no}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
