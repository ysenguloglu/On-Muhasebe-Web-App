"""
Veritabanı bağlantı yönetimi
SQLite veritabanı bağlantı işlemleri
"""
import sqlite3
import os


class DatabaseConnection:
    """SQLite veritabanı bağlantı yönetim sınıfı"""
    
    def __init__(self, db_path: str = "on_muhasebe.db"):
        """
        Veritabanı bağlantısı oluştur
        
        Args:
            db_path: Veritabanı dosya yolu
        """
        self.db_path = db_path
        self.conn = None
    
    def connect(self):
        """Veritabanı bağlantısı oluştur - Thread-safe"""
        # Her çağrıda yeni bir connection oluştur (thread-safe için)
        # Eğer eski connection varsa kapat
        if self.conn:
            try:
                self.conn.close()
            except:
                pass
            finally:
                self.conn = None
        
        # Yeni bağlantı oluştur - check_same_thread=False ile thread-safe
        self.conn = sqlite3.connect(
            self.db_path, 
            timeout=20.0,
            check_same_thread=False  # Thread-safe için
        )
        self.conn.row_factory = sqlite3.Row
        
        # Basit ve güvenilir ayarlar
        self.conn.execute("PRAGMA busy_timeout=20000")  # 20 saniye bekleme
        self.conn.execute("PRAGMA synchronous=NORMAL")  # Hızlı ve güvenli
        self.conn.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging (daha iyi concurrency)
        
        return self.conn
    
    def close(self):
        """Veritabanı bağlantısını kapat"""
        if self.conn:
            try:
                self.conn.close()
            except:
                pass
            finally:
                self.conn = None
    
    def init_database(self):
        """Veritabanı tablolarını oluştur"""
        conn = self.connect()
        cursor = conn.cursor()
        
        # Stok tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stok (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                urun_kodu TEXT UNIQUE,
                urun_adi TEXT NOT NULL,
                marka TEXT,
                birim TEXT DEFAULT 'Adet',
                stok_miktari REAL DEFAULT 0,
                birim_fiyat REAL DEFAULT 0,
                aciklama TEXT,
                olusturma_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                guncelleme_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Cari hesap tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cari (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cari_kodu TEXT UNIQUE,
                unvan TEXT NOT NULL,
                tip TEXT NOT NULL CHECK(tip IN ('Müşteri', 'Tedarikçi')),
                telefon TEXT,
                email TEXT,
                adres TEXT,
                tc_kimlik_no TEXT UNIQUE,
                vergi_no TEXT,
                vergi_dairesi TEXT,
                bakiye REAL DEFAULT 0,
                aciklama TEXT,
                olusturma_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                guncelleme_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # İş evrakı tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS is_evraki (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                is_emri_no INTEGER NOT NULL,
                tarih TEXT NOT NULL,
                musteri_unvan TEXT NOT NULL,
                telefon TEXT,
                arac_plakasi TEXT,
                cekici_dorse TEXT,
                marka_model TEXT,
                talep_edilen_isler TEXT,
                musteri_sikayeti TEXT,
                yapilan_is TEXT,
                baslama_saati TEXT,
                bitis_saati TEXT,
                kullanilan_urunler TEXT,
                toplam_tutar REAL DEFAULT 0,
                tc_kimlik_no TEXT,
                olusturma_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Migration: Eski veritabanları için kolon ekleme (sadece gerektiğinde)
        try:
            cursor.execute("ALTER TABLE stok ADD COLUMN marka TEXT")
        except sqlite3.OperationalError:
            pass
        
        try:
            cursor.execute("ALTER TABLE cari ADD COLUMN tc_kimlik_no TEXT UNIQUE")
        except sqlite3.OperationalError:
            pass
        
        try:
            cursor.execute("ALTER TABLE is_evraki ADD COLUMN tc_kimlik_no TEXT")
        except sqlite3.OperationalError:
            pass
        
        # Migration: firma_tipi kolonu ekle (varsayılan: 'Şahıs')
        try:
            cursor.execute("ALTER TABLE cari ADD COLUMN firma_tipi TEXT DEFAULT 'Şahıs'")
            # Mevcut kayıtlar için varsayılan değer ata
            cursor.execute("UPDATE cari SET firma_tipi = 'Şahıs' WHERE firma_tipi IS NULL")
        except sqlite3.OperationalError:
            pass
        
        conn.commit()
        self.close()

