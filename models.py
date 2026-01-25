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
    musteri_email: Optional[str] = ""
    musteri_adres: Optional[str] = ""
    vergi_dairesi: Optional[str] = ""
    firma_tipi: Optional[str] = "Şahıs"
    send_email: Optional[bool] = True


class IsProsesiMaddeCreate(BaseModel):
    sira_no: int
    madde_adi: str
    aciklama: Optional[str] = ""


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
    tamamlandi: Optional[bool] = False
