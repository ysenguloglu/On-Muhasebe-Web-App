"""
Pydantic models for API requests/responses
"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class StokCreate(BaseModel):
    urun_kodu: Optional[str] = None
    urun_adi: str
    marka: Optional[str] = ""
    birim: Optional[str] = "Adet"
    stok_miktari: Optional[float] = 0
    birim_fiyat: Optional[float] = 0
    aciklama: Optional[str] = ""


class StokUpdate(BaseModel):
    urun_kodu: Optional[str] = None
    urun_adi: str
    marka: Optional[str] = ""
    birim: Optional[str] = "Adet"
    stok_miktari: Optional[float] = 0
    birim_fiyat: Optional[float] = 0
    aciklama: Optional[str] = ""


class StokMiktarAzalt(BaseModel):
    urun_kodu: str
    miktar: float


class StokMiktarAzaltBatch(BaseModel):
    urunler: List[Dict[str, Any]]


class CariCreate(BaseModel):
    cari_kodu: Optional[str] = None
    unvan: str
    tip: str
    telefon: Optional[str] = ""
    email: Optional[str] = ""
    adres: Optional[str] = ""
    tc_kimlik_no: Optional[str] = ""
    vergi_no: Optional[str] = ""
    vergi_dairesi: Optional[str] = ""
    bakiye: Optional[float] = 0
    aciklama: Optional[str] = ""
    firma_tipi: Optional[str] = "Şahıs"


class CariUpdate(BaseModel):
    cari_kodu: Optional[str] = None
    unvan: str
    tip: str
    telefon: Optional[str] = ""
    email: Optional[str] = ""
    adres: Optional[str] = ""
    vergi_no: Optional[str] = ""
    vergi_dairesi: Optional[str] = ""
    bakiye: Optional[float] = 0
    aciklama: Optional[str] = ""
    firma_tipi: Optional[str] = "Şahıs"


class IsEvrakiCreate(BaseModel):
    is_emri_no: int
    tarih: str
    musteri_unvan: str
    telefon: Optional[str] = ""
    arac_plakasi: Optional[str] = ""
    cekici_dorse: Optional[str] = ""
    marka_model: Optional[str] = ""
    talep_edilen_isler: Optional[str] = ""
    musteri_sikayeti: Optional[str] = ""
    yapilan_is: Optional[str] = ""
    baslama_saati: Optional[str] = ""
    bitis_saati: Optional[str] = ""
    kullanilan_urunler: Optional[str] = ""
    toplam_tutar: Optional[float] = 0
    tc_kimlik_no: Optional[str] = ""
    odeme_durumu: Optional[str] = "odenmedi"


class IsEvrakiCreateWithEmail(BaseModel):
    is_emri_no: int
    tarih: str
    musteri_unvan: str
    telefon: Optional[str] = ""
    arac_plakasi: Optional[str] = ""
    cekici_dorse: Optional[str] = ""
    marka_model: Optional[str] = ""
    talep_edilen_isler: Optional[str] = ""
    musteri_sikayeti: Optional[str] = ""
    yapilan_is: Optional[str] = ""
    baslama_saati: Optional[str] = ""
    bitis_saati: Optional[str] = ""
    kullanilan_urunler: Optional[str] = ""
    toplam_tutar: Optional[float] = 0
    tc_kimlik_no: Optional[str] = ""
    odeme_durumu: Optional[str] = "odenmedi"
    musteri_email: Optional[str] = ""
    musteri_adres: Optional[str] = ""
    vergi_dairesi: Optional[str] = ""
    firma_tipi: Optional[str] = "Şahıs"
    send_email: Optional[bool] = True


class IsEvrakiUpdate(BaseModel):
    is_emri_no: int
    tarih: str
    musteri_unvan: str
    telefon: Optional[str] = ""
    arac_plakasi: Optional[str] = ""
    cekici_dorse: Optional[str] = ""
    marka_model: Optional[str] = ""
    talep_edilen_isler: Optional[str] = ""
    musteri_sikayeti: Optional[str] = ""
    yapilan_is: Optional[str] = ""
    baslama_saati: Optional[str] = ""
    bitis_saati: Optional[str] = ""
    kullanilan_urunler: Optional[str] = ""
    toplam_tutar: Optional[float] = 0
    tc_kimlik_no: Optional[str] = ""
    odeme_durumu: Optional[str] = "odenmedi"


class IsEvrakiUpdateWithEmail(BaseModel):
    is_emri_no: int
    tarih: str
    musteri_unvan: str
    telefon: Optional[str] = ""
    arac_plakasi: Optional[str] = ""
    cekici_dorse: Optional[str] = ""
    marka_model: Optional[str] = ""
    talep_edilen_isler: Optional[str] = ""
    musteri_sikayeti: Optional[str] = ""
    yapilan_is: Optional[str] = ""
    baslama_saati: Optional[str] = ""
    bitis_saati: Optional[str] = ""
    kullanilan_urunler: Optional[str] = ""
    toplam_tutar: Optional[float] = 0
    tc_kimlik_no: Optional[str] = ""
    odeme_durumu: Optional[str] = "odenmedi"
    musteri_email: Optional[str] = ""
    musteri_adres: Optional[str] = ""
    vergi_dairesi: Optional[str] = ""
    firma_tipi: Optional[str] = "Şahıs"
    send_email: Optional[bool] = True


class IsProsesiMaddeCreate(BaseModel):
    sira_no: int
    madde_adi: str
    aciklama: Optional[str] = ""
    kullanilan_malzemeler: Optional[str] = ""


PROSES_TIPLERI = ("Söküm", "Temizlik", "Revizyon", "Montaj")


class IsProsesiCreate(BaseModel):
    proses_adi: str
    proses_tipi: Optional[str] = None  # Söküm, Temizlik, Revizyon, Montaj
    aciklama: Optional[str] = ""
    maddeler: Optional[List[IsProsesiMaddeCreate]] = []


class IsProsesiUpdate(BaseModel):
    proses_adi: str
    proses_tipi: Optional[str] = None  # Söküm, Temizlik, Revizyon, Montaj
    aciklama: Optional[str] = ""


class IsProsesiMaddeUpdate(BaseModel):
    sira_no: int
    madde_adi: str
    aciklama: Optional[str] = ""
    kullanilan_malzemeler: Optional[str] = ""
    tamamlandi: Optional[bool] = False


# ---------- Araç Yönetimi (Modül 2) ----------
# Sabitler (API dokümantasyonu için)
ARAC_TIPLERI = ("çekici", "dorse", "diğer")
ARAC_DURUMLARI = ("aktif", "bakımda", "pasif")
ARAC_BELGE_TURLERI = (
    "araç muayenesi",
    "trafik sigortası",
    "kasko",
    "egzoz muayenesi",
    "ADR sertifikası",
    "araç ruhsatı",
)
ARAC_BAKIM_TURLERI = ("yağ değişimi", "fren kontrolü", "lastik değişimi", "genel bakım")


class AracCreate(BaseModel):
    arac_plakasi: str
    arac_tipi: Optional[str] = "diğer"
    marka: Optional[str] = ""
    model: Optional[str] = ""
    model_yili: Optional[int] = None
    sasi_no: Optional[str] = ""
    motor_no: Optional[str] = ""
    guncel_km: Optional[float] = 0
    alis_tarihi: Optional[str] = None
    alis_fiyati: Optional[float] = None
    durum: Optional[str] = "aktif"


class AracUpdate(BaseModel):
    arac_plakasi: str
    arac_tipi: Optional[str] = "diğer"
    marka: Optional[str] = ""
    model: Optional[str] = ""
    model_yili: Optional[int] = None
    sasi_no: Optional[str] = ""
    motor_no: Optional[str] = ""
    guncel_km: Optional[float] = 0
    alis_tarihi: Optional[str] = None
    alis_fiyati: Optional[float] = None
    durum: Optional[str] = "aktif"


class AracBelgeCreate(BaseModel):
    belge_turu: str
    duzenlenme_tarihi: Optional[str] = None
    bitis_tarihi: str
    belge_dosya_path: Optional[str] = None


class AracBakimCreate(BaseModel):
    bakim_turu: str
    aciklama: Optional[str] = ""
    bakim_tarihi: Optional[str] = ""
    bakim_km: Optional[float] = None
    maliyet: Optional[float] = None


class SoforCreate(BaseModel):
    """Şoför kaydı. Tarih alanları (YYYY-MM-DD) ileride uyarı/son tarih kontrolleri için DATE ile saklanır."""
    ad_soyad: str
    tc_kimlik_no: str
    telefon: str
    email: Optional[str] = ""
    adres: Optional[str] = ""
    ise_baslama_tarihi: str
    src_belge_no: str
    src_bitis_tarihi: str
    ehliyet_sinifi: str
    ehliyet_bitis_tarihi: str
    psikoteknik_bitis: str
    acil_iletisim: str
    iban: Optional[str] = ""
    durum: Optional[str] = "aktif"


class SoforUpdate(BaseModel):
    ad_soyad: str
    tc_kimlik_no: str
    telefon: str
    email: Optional[str] = ""
    adres: Optional[str] = ""
    ise_baslama_tarihi: str
    src_belge_no: str
    src_bitis_tarihi: str
    ehliyet_sinifi: str
    ehliyet_bitis_tarihi: str
    psikoteknik_bitis: str
    acil_iletisim: str
    iban: Optional[str] = ""
    durum: Optional[str] = "aktif"
