"""
Veritabanı yönetim modülü - Ana sınıf
Tüm veritabanı işlemlerini birleştirir
"""
from .db_connection import DatabaseConnection
from .db_stok import StokDB
from .db_cari import CariDB
from .db_is_evraki import IsEvrakiDB


class Database:
    """SQLite veritabanı yönetim sınıfı - Tüm modülleri birleştirir"""
    
    def __init__(self, db_path: str = "on_muhasebe.db"):
        """
        Veritabanı bağlantısı oluştur
        
        Args:
            db_path: Veritabanı dosya yolu
        """
        self.db_conn = DatabaseConnection(db_path)
        self.db_conn.init_database()
        
        # Alt modülleri başlat
        self.stok = StokDB(self.db_conn)
        self.cari = CariDB(self.db_conn)
        self.is_evraki = IsEvrakiDB(self.db_conn)
    
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
    
    # ========== BAĞLANTI YÖNETİMİ (Delegasyon) ==========
    
    def connect(self):
        return self.db_conn.connect()
    
    def close(self):
        return self.db_conn.close()
