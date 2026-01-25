"""
İş Evrakı (Work Order) API endpoints
"""
from fastapi import APIRouter, HTTPException
import json
from decimal import Decimal
from datetime import date, datetime

from models import IsEvrakiCreate, IsEvrakiCreateWithEmail, IsEvrakiUpdate, IsEvrakiUpdateWithEmail
from api.pdf_email import pdf_olustur_api, email_gonder_api
from db_instance import db

router = APIRouter(prefix="/api/is-evraki", tags=["is-evraki"])


def _evrak_json_serialize(obj):
    """MySQL'den gelen Decimal, datetime gibi JSON'a uyumsuz tipleri dönüştür."""
    if obj is None:
        return None
    if isinstance(obj, (list, tuple)):
        return [_evrak_json_serialize(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _evrak_json_serialize(v) for k, v in obj.items()}
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, (datetime, date)):
        return obj.isoformat() if obj else None
    return obj


@router.get("/sonraki-no")
async def is_emri_no_sonraki():
    """Get next available work order number"""
    try:
        no = db.is_emri_no_sonraki()
        return {"success": True, "data": {"is_emri_no": no}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("")
async def is_evraki_listele():
    """List all work orders"""
    try:
        evraklar = db.is_evraki_listele()
        evraklar = _evrak_json_serialize(evraklar)
        return {"success": True, "data": evraklar, "count": len(evraklar)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{evrak_id}")
async def is_evraki_getir(evrak_id: int):
    """Get a specific work order by ID"""
    try:
        evrak = db.is_evraki_getir(evrak_id)
        if not evrak:
            raise HTTPException(status_code=404, detail="İş evrakı bulunamadı")
        evrak = _evrak_json_serialize(evrak)
        return {"success": True, "data": evrak}
    except HTTPException:
        raise
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


@router.put("/{evrak_id}")
async def is_evraki_guncelle(evrak_id: int, evrak: IsEvrakiUpdate):
    """Update a work order"""
    try:
        if not evrak.musteri_unvan:
            raise HTTPException(status_code=400, detail="Müşteri ünvanı zorunludur")
        
        basarili, mesaj = db.is_evraki_guncelle(
            evrak_id, evrak.is_emri_no, evrak.tarih, evrak.musteri_unvan, evrak.telefon,
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


@router.put("/guncelle-ve-gonder/{evrak_id}")
async def is_evraki_guncelle_ve_gonder(evrak_id: int, evrak: IsEvrakiUpdateWithEmail):
    """İş evrakını güncelle, PDF oluştur ve e-posta gönder"""
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
        
        # İş evrakını veritabanında güncelle
        basarili, hata_mesaji = db.is_evraki_guncelle(
            evrak_id, evrak.is_emri_no, evrak.tarih, evrak.musteri_unvan, evrak.telefon,
            evrak.arac_plakasi, evrak.cekici_dorse, evrak.marka_model,
            evrak.talep_edilen_isler, evrak.musteri_sikayeti, evrak.yapilan_is,
            evrak.baslama_saati, evrak.bitis_saati, evrak.kullanilan_urunler,
            evrak.toplam_tutar, evrak.tc_kimlik_no
        )
        
        if not basarili:
            raise HTTPException(status_code=400, detail=f"İş evrakı güncellenemedi: {hata_mesaji}")
        
        # PDF oluştur ve e-posta gönder
        pdf_path = None
        email_sent = False
        
        if evrak.send_email:
            try:
                # IsEvrakiCreateWithEmail formatına çevir
                evrak_with_email = IsEvrakiCreateWithEmail(
                    is_emri_no=evrak.is_emri_no,
                    tarih=evrak.tarih,
                    musteri_unvan=evrak.musteri_unvan,
                    telefon=evrak.telefon,
                    arac_plakasi=evrak.arac_plakasi,
                    cekici_dorse=evrak.cekici_dorse,
                    marka_model=evrak.marka_model,
                    talep_edilen_isler=evrak.talep_edilen_isler,
                    musteri_sikayeti=evrak.musteri_sikayeti,
                    yapilan_is=evrak.yapilan_is,
                    baslama_saati=evrak.baslama_saati,
                    bitis_saati=evrak.bitis_saati,
                    kullanilan_urunler=evrak.kullanilan_urunler,
                    toplam_tutar=evrak.toplam_tutar,
                    tc_kimlik_no=evrak.tc_kimlik_no,
                    musteri_email=evrak.musteri_email,
                    musteri_adres=evrak.musteri_adres,
                    vergi_dairesi=evrak.vergi_dairesi,
                    firma_tipi=evrak.firma_tipi,
                    send_email=evrak.send_email
                )
                
                pdf_path = await pdf_olustur_api(evrak_with_email, urunler)
                if pdf_path:
                    email_sent = await email_gonder_api(evrak_with_email, pdf_path)
                    # PDF dosyasını temizle (geçici dosya)
                    try:
                        if os.path.exists(pdf_path):
                            os.remove(pdf_path)
                    except:
                        pass
            except Exception as e:
                # PDF/Email hatası olsa bile güncelleme başarılı
                return {
                    "success": True,
                    "message": "İş evrakı güncellendi ancak PDF/e-posta gönderiminde hata oluştu",
                    "warning": str(e),
                    "email_sent": False
                }
        
        return {
            "success": True,
            "message": "İş evrakı başarıyla güncellendi" + (" ve e-posta gönderildi" if email_sent else ""),
            "email_sent": email_sent
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/gonder/{evrak_id}")
async def is_evraki_gonder(evrak_id: int):
    """Kayıtlı iş evrakını e-posta ile gönder"""
    import os
    
    try:
        # İş evrakını veritabanından getir
        evrak = db.is_evraki_getir(evrak_id)
        if not evrak:
            raise HTTPException(status_code=404, detail="İş evrakı bulunamadı")
        
        # Kullanılan ürünleri parse et
        urunler = []
        if evrak.get('kullanilan_urunler'):
            try:
                urunler = json.loads(evrak['kullanilan_urunler'])
            except:
                pass
        
        # Cari hesaptan müşteri bilgilerini al
        musteri_email = ""
        musteri_adres = ""
        vergi_dairesi = ""
        firma_tipi = "Şahıs"
        
        if evrak.get('musteri_unvan'):
            cari = db.cari_unvan_ile_ara(evrak['musteri_unvan'])
            if cari:
                musteri_email = cari.get('email', '')
                musteri_adres = cari.get('adres', '')
                vergi_dairesi = cari.get('vergi_dairesi', '')
                firma_tipi = cari.get('firma_tipi', 'Şahıs')
        
        # IsEvrakiCreateWithEmail formatına çevir
        evrak_with_email = IsEvrakiCreateWithEmail(
            is_emri_no=evrak.get('is_emri_no', 0),
            tarih=evrak.get('tarih', ''),
            musteri_unvan=evrak.get('musteri_unvan', ''),
            telefon=evrak.get('telefon', ''),
            arac_plakasi=evrak.get('arac_plakasi', ''),
            cekici_dorse=evrak.get('cekici_dorse', ''),
            marka_model=evrak.get('marka_model', ''),
            talep_edilen_isler=evrak.get('talep_edilen_isler', ''),
            musteri_sikayeti=evrak.get('musteri_sikayeti', ''),
            yapilan_is=evrak.get('yapilan_is', ''),
            baslama_saati=evrak.get('baslama_saati', ''),
            bitis_saati=evrak.get('bitis_saati', ''),
            kullanilan_urunler=evrak.get('kullanilan_urunler', ''),
            toplam_tutar=evrak.get('toplam_tutar', 0),
            tc_kimlik_no=evrak.get('tc_kimlik_no', ''),
            musteri_email=musteri_email,
            musteri_adres=musteri_adres,
            vergi_dairesi=vergi_dairesi,
            firma_tipi=firma_tipi,
            send_email=True
        )
        
        # PDF oluştur ve e-posta gönder
        pdf_path = None
        email_sent = False
        
        try:
            pdf_path = await pdf_olustur_api(evrak_with_email, urunler)
            if pdf_path:
                email_sent = await email_gonder_api(evrak_with_email, pdf_path)
                # PDF dosyasını temizle (geçici dosya)
                try:
                    if os.path.exists(pdf_path):
                        os.remove(pdf_path)
                except:
                    pass
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"PDF/e-posta gönderiminde hata: {str(e)}")
        
        if email_sent:
            return {
                "success": True,
                "message": "E-posta başarıyla gönderildi",
                "email_sent": True
            }
        else:
            raise HTTPException(status_code=500, detail="E-posta gönderilemedi")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{evrak_id}")
async def is_evraki_sil(evrak_id: int):
    """Delete a work order"""
    try:
        basarili, mesaj = db.is_evraki_sil(evrak_id)
        if basarili:
            return {"success": True, "message": mesaj}
        else:
            raise HTTPException(status_code=404, detail=mesaj)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
