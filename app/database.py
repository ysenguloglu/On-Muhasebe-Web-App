"""
Veritabanı yönetim modülü - Ana sınıf
Tüm veritabanı işlemlerini birleştirir
"""
from .db_connection import DatabaseConnection
from .db_stok import StokDB
from .db_cari import CariDB
from .db_is_evraki import IsEvrakiDB
from .db_is_prosesi import IsProsesiDB


class Database:
    """Veritabanı yönetim sınıfı - MySQL - Tüm modülleri birleştirir"""

    def __init__(self, database_url: str):
        """
        MySQL bağlantısı. database_url zorunludur.
        """
        self.db_conn = DatabaseConnection(database_url=database_url)

        try:
            print("🔄 Veritabanı başlatılıyor (MySQL)...")
            self.db_conn.init_database()
        except Exception as e:
            print(f"❌ Veritabanı hatası: {e}")
            import traceback
            traceback.print_exc()
            # Hata olsa bile devam et, belki tablolar zaten var
            # Ama uygulama başlarken tekrar kontrol edilecek
        
        # Alt modülleri başlat
        self.stok = StokDB(self.db_conn)
        self.cari = CariDB(self.db_conn)
        self.is_evraki = IsEvrakiDB(self.db_conn)
        self.is_prosesi = IsProsesiDB(self.db_conn)
    
    # ========== STOK İŞLEMLERİ (Delegasyon) ==========
    
    def stok_ekle(self, *args, **kwargs):
        return self.stok.stok_ekle(*args, **kwargs)
    
    def stok_guncelle(self, *args, **kwargs):
        return self.stok.stok_guncelle(*args, **kwargs)
    
    def stok_sil(self, *args, **kwargs):
        return self.stok.stok_sil(*args, **kwargs)
    
    def stok_listele(self, *args, **kwargs):
        return self.stok.stok_listele(*args, **kwargs)
    
    def stok_getir(self, *args, **kwargs):
        return self.stok.stok_getir(*args, **kwargs)
    
    def stok_urun_adi_ile_ara(self, *args, **kwargs):
        return self.stok.stok_urun_adi_ile_ara(*args, **kwargs)
    
    def stok_urun_kodu_ile_ara(self, *args, **kwargs):
        return self.stok.stok_urun_kodu_ile_ara(*args, **kwargs)
    
    def stok_miktar_azalt(self, *args, **kwargs):
        return self.stok.stok_miktar_azalt(*args, **kwargs)
    
    def stok_miktar_azalt_batch(self, *args, **kwargs):
        return self.stok.stok_miktar_azalt_batch(*args, **kwargs)
    
    # ========== CARİ İŞLEMLERİ (Delegasyon) ==========
    
    def cari_ekle(self, *args, **kwargs):
        return self.cari.cari_ekle(*args, **kwargs)
    
    def cari_guncelle(self, *args, **kwargs):
        return self.cari.cari_guncelle(*args, **kwargs)
    
    def cari_sil(self, *args, **kwargs):
        return self.cari.cari_sil(*args, **kwargs)
    
    def cari_listele(self, *args, **kwargs):
        return self.cari.cari_listele(*args, **kwargs)
    
    def cari_getir(self, *args, **kwargs):
        return self.cari.cari_getir(*args, **kwargs)
    
    def cari_tc_ile_ara(self, *args, **kwargs):
        return self.cari.cari_tc_ile_ara(*args, **kwargs)
    
    def cari_unvan_ile_ara(self, *args, **kwargs):
        return self.cari.cari_unvan_ile_ara(*args, **kwargs)
    
    def cari_sonraki_kod_olustur(self, *args, **kwargs):
        return self.cari.cari_sonraki_kod_olustur(*args, **kwargs)
    
    def cari_ekle_tc_kontrolu_ile(self, *args, **kwargs):
        return self.cari.cari_ekle_tc_kontrolu_ile(*args, **kwargs)
    
    # ========== İŞ EVRAKI İŞLEMLERİ (Delegasyon) ==========
    
    def is_evraki_ekle(self, *args, **kwargs):
        return self.is_evraki.is_evraki_ekle(*args, **kwargs)
    
    def is_evraki_listele(self, *args, **kwargs):
        return self.is_evraki.is_evraki_listele(*args, **kwargs)
    
    def is_evraki_getir(self, *args, **kwargs):
        return self.is_evraki.is_evraki_getir(*args, **kwargs)
    
    def is_evraki_guncelle(self, *args, **kwargs):
        return self.is_evraki.is_evraki_guncelle(*args, **kwargs)
    
    def is_evraki_sil(self, *args, **kwargs):
        return self.is_evraki.is_evraki_sil(*args, **kwargs)
    
    def is_emri_no_sonraki(self, *args, **kwargs):
        return self.is_evraki.is_emri_no_sonraki(*args, **kwargs)

    def is_evraki_aylik_getir(self, *args, **kwargs):
        return self.is_evraki.is_evraki_aylik_getir(*args, **kwargs)
    
    # ========== İŞ PROSESİ İŞLEMLERİ (Delegasyon) ==========
    
    def is_prosesi_ekle(self, *args, **kwargs):
        return self.is_prosesi.is_prosesi_ekle(*args, **kwargs)
    
    def is_prosesi_listele(self, *args, **kwargs):
        return self.is_prosesi.is_prosesi_listele(*args, **kwargs)
    
    def is_prosesi_getir(self, *args, **kwargs):
        return self.is_prosesi.is_prosesi_getir(*args, **kwargs)
    
    def is_prosesi_guncelle(self, *args, **kwargs):
        return self.is_prosesi.is_prosesi_guncelle(*args, **kwargs)
    
    def is_prosesi_sil(self, *args, **kwargs):
        return self.is_prosesi.is_prosesi_sil(*args, **kwargs)
    
    def is_prosesi_madde_ekle(self, *args, **kwargs):
        return self.is_prosesi.is_prosesi_madde_ekle(*args, **kwargs)
    
    def is_prosesi_maddeleri_getir(self, *args, **kwargs):
        return self.is_prosesi.is_prosesi_maddeleri_getir(*args, **kwargs)
    
    def is_prosesi_madde_guncelle(self, *args, **kwargs):
        return self.is_prosesi.is_prosesi_madde_guncelle(*args, **kwargs)
    
    def is_prosesi_madde_sil(self, *args, **kwargs):
        return self.is_prosesi.is_prosesi_madde_sil(*args, **kwargs)
    
    def is_prosesi_tamamla_madde(self, *args, **kwargs):
        return self.is_prosesi.is_prosesi_tamamla_madde(*args, **kwargs)
    
    # ========== BAĞLANTI YÖNETİMİ (Delegasyon) ==========
    
    def connect(self):
        return self.db_conn.connect()
    
    def close(self):
        return self.db_conn.close()
