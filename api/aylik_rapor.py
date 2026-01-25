"""
Aylık iş evrakları raporu: PDF oluşturup EMAIL_TO adresine gönderir.
Müşteri sayısı, ciro, ürün bazlı kullanım özeti.
"""
import json
import os
from datetime import date
from collections import defaultdict
from typing import Tuple

from fastapi import APIRouter, HTTPException, Header, Query

from db_instance import db
from api.pdf_email import aylik_rapor_pdf_olustur, rapor_email_gonder

router = APIRouter(prefix="/api/aylik-rapor", tags=["aylik-rapor"])


def _onceki_ay() -> Tuple[int, int]:
    """Önceki ay ve yıl (bugüne göre)."""
    bugun = date.today()
    if bugun.month == 1:
        return 12, bugun.year - 1
    return bugun.month - 1, bugun.year


def _urun_ozetleri(evraklar: list) -> list:
    """Evraklardan kullanilan_urunler JSON'larını parse edip ürün bazlı toplam adet ve toplam tutar hesaplar."""
    # key: (urun_kodu, urun_adi) -> { toplam_adet, toplam_tutar }
    agg = defaultdict(lambda: {"toplam_adet": 0.0, "toplam_tutar": 0.0})
    for e in evraklar:
        raw = e.get("kullanilan_urunler") or ""
        if not raw:
            continue
        try:
            arr = json.loads(raw) if isinstance(raw, str) else raw
        except Exception:
            continue
        if not isinstance(arr, list):
            continue
        for u in arr:
            if not isinstance(u, dict):
                continue
            adet = float(u.get("adet") or 0)
            toplam = float(u.get("toplam") or 0)
            kod = (u.get("urun_kodu") or "").strip() or "-"
            adi = (u.get("urun_adi") or "").strip() or "-"
            key = (kod, adi)
            agg[key]["toplam_adet"] += adet
            agg[key]["toplam_tutar"] += toplam
    return [
        {"urun_kodu": k[0], "urun_adi": k[1], "toplam_adet": v["toplam_adet"], "toplam_tutar": v["toplam_tutar"]}
        for k, v in sorted(agg.items(), key=lambda x: (-x[1]["toplam_tutar"], x[0][1]))
    ]


async def run_aylik_rapor(ay: int, yil: int) -> dict:
    """
    Aylık raporu oluşturup EMAIL_TO adresine gönderir.
    Endpoint ve otomatik cron job tarafından kullanılır. Hata durumunda exception fırlatır.
    """
    evraklar = db.is_evraki_aylik_getir(ay, yil)
    musteri_sayisi = len(set((e.get("musteri_unvan") or "").strip() for e in evraklar if (e.get("musteri_unvan") or "").strip()))
    ciro = sum(float(e.get("toplam_tutar") or 0) for e in evraklar)
    urun_detay = _urun_ozetleri(evraklar)

    pdf_path = await aylik_rapor_pdf_olustur(ay, yil, musteri_sayisi, ciro, urun_detay)
    if not pdf_path:
        raise Exception("PDF oluşturulamadı.")
    await rapor_email_gonder(pdf_path, ay, yil)
    if os.path.exists(pdf_path):
        try:
            os.remove(pdf_path)
        except Exception:
            pass

    ay_adi = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
              "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"][ay - 1]
    return {
        "success": True,
        "message": f"{ay_adi} {yil} aylık rapor PDF olarak {os.getenv('EMAIL_TO', '')} adresine gönderildi.",
        "ay": ay,
        "yil": yil,
        "musteri_sayisi": musteri_sayisi,
        "ciro": round(ciro, 2),
        "evrak_sayisi": len(evraklar),
        "email_sent": True,
    }


async def aylik_rapor_cron_job():
    """
    Otomatik cron job: Bir önceki aya ait raporu oluşturup gönderir.
    Her ayın 1'inde 09:00 (Türkiye saati) çalışacak şekilde main.py'de zamanlanır.
    """
    a, y = _onceki_ay()
    try:
        await run_aylik_rapor(a, y)
        print(f"✅ Aylık rapor (otomatik): {a}/{y} — e-posta gönderildi.")
    except Exception as e:
        print(f"❌ Aylık rapor (otomatik) hatası {a}/{y}: {e}")
        import traceback
        traceback.print_exc()


@router.post("/gonder")
async def aylik_rapor_gonder(
    ay: int = Query(None, description="Ay (1-12). Verilmezse önceki ay."),
    yil: int = Query(None, description="Yıl. Verilmezse önceki ayın yılı."),
    secret: str = Query(None, description="CRON_SECRET ile eşleşmeli (opsiyonel)."),
    x_cron_secret: str = Header(None, alias="X-Cron-Secret"),
):
    """
    Aylık iş evrakları özet raporunu PDF olarak oluşturup EMAIL_TO adresine gönderir.
    İçerik: müşteri sayısı, toplam ciro, ürün bazlı kullanım.
    Otomatik çağrı için: CRON_SECRET tanımlıysa, secret veya X-Cron-Secret ile eşleşmeli.
    """
    cron_secret = os.getenv("CRON_SECRET", "")
    if cron_secret:
        provided = secret or x_cron_secret
        if provided != cron_secret:
            raise HTTPException(status_code=403, detail="Geçersiz veya eksik CRON_SECRET.")

    a, y = (ay, yil) if ay is not None and yil is not None else _onceki_ay()
    if not (1 <= a <= 12) or not (2000 <= y <= 2100):
        raise HTTPException(status_code=400, detail="Geçersiz ay veya yıl.")

    try:
        return await run_aylik_rapor(a, y)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
