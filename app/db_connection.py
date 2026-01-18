"""
Veritabanı bağlantı yönetimi
SQLite ve PostgreSQL veritabanı bağlantı işlemleri
"""
import os
import sqlite3
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# PostgreSQL için psycopg2 import (opsiyonel)
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    from psycopg2 import pool
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False


class DatabaseConnection:
    """Veritabanı bağlantı yönetim sınıfı - SQLite ve PostgreSQL desteği"""
    
    def __init__(self, db_path: Optional[str] = None, database_url: Optional[str] = None):
        """
        Veritabanı bağlantısı oluştur
        
        Args:
            db_path: SQLite veritabanı dosya yolu (SQLite için)
            database_url: PostgreSQL connection string (PostgreSQL için)
        """
        self.database_url = database_url or os.getenv("DATABASE_URL")
        self.db_path = db_path or "on_muhasebe.db"
        self.conn = None
        self.is_postgres = False
        
        # DATABASE_URL varsa PostgreSQL kullan
        # Railway bazen postgres:// veya postgresql:// formatında URL verebilir
        if self.database_url and (self.database_url.startswith("postgresql://") or self.database_url.startswith("postgres://")):
            # postgres:// formatını postgresql:// formatına çevir (psycopg2 için)
            if self.database_url.startswith("postgres://"):
                self.database_url = self.database_url.replace("postgres://", "postgresql://", 1)
            self.is_postgres = True
            if not PSYCOPG2_AVAILABLE:
                raise ImportError("PostgreSQL kullanmak için psycopg2-binary paketi yüklü olmalı")
    
    def connect(self):
        """Veritabanı bağlantısı oluştur - Thread-safe"""
        # Eğer eski connection varsa kapat
        if self.conn:
            try:
                self.conn.close()
            except:
                pass
            finally:
                self.conn = None
        
        if self.is_postgres:
            # PostgreSQL bağlantısı
            self.conn = psycopg2.connect(self.database_url)
            # PostgreSQL için search_path'i public olarak ayarla
            cursor = self.conn.cursor()
            cursor.execute("SET search_path TO public;")
            self.conn.commit()
            cursor.close()
            return self.conn
        else:
            # SQLite bağlantısı
            self.conn = sqlite3.connect(
                self.db_path, 
                timeout=20.0,
                check_same_thread=False
            )
            self.conn.row_factory = sqlite3.Row
            
            # SQLite ayarları
            self.conn.execute("PRAGMA busy_timeout=20000")
            self.conn.execute("PRAGMA synchronous=NORMAL")
            self.conn.execute("PRAGMA journal_mode=WAL")
            
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
    
    def _get_cursor(self):
        """Cursor oluştur - PostgreSQL için RealDictCursor, SQLite için normal cursor"""
        conn = self.connect()
        if self.is_postgres:
            return conn.cursor(cursor_factory=RealDictCursor)
        else:
            return conn.cursor()
    
    def _convert_placeholders(self, query: str) -> str:
        """Placeholder'ları veritabanı tipine göre dönüştür (? -> %s PostgreSQL için)"""
        if self.is_postgres:
            # PostgreSQL için ? -> %s
            return query.replace('?', '%s')
        return query  # SQLite için ? olduğu gibi kalır
    
    def _execute_query(self, query: str, params: tuple = None):
        """Query çalıştır - Her iki veritabanı için uyumlu"""
        cursor = self._get_cursor()
        try:
            query = self._convert_placeholders(query)
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor
        except Exception as e:
            self.close()
            raise e
    
    def _is_integrity_error(self, exception: Exception) -> bool:
        """Integrity error kontrolü - Her iki veritabanı için"""
        if self.is_postgres:
            # PostgreSQL için psycopg2.errors.UniqueViolation veya IntegrityError
            try:
                import psycopg2
                import psycopg2.errors
                return isinstance(exception, (psycopg2.errors.UniqueViolation, psycopg2.IntegrityError, psycopg2.errors.IntegrityError))
            except:
                # Eğer psycopg2 import edilemezse, exception tipine bak
                return 'unique' in str(exception).lower() or 'integrity' in str(exception).lower()
        else:
            # SQLite için
            return isinstance(exception, sqlite3.IntegrityError)
    
    def init_database(self):
        """Veritabanı tablolarını oluştur"""
        conn = None
        cursor = None
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            if self.is_postgres:
                # PostgreSQL için schema'yı ayarla (varsayılan: public)
                cursor.execute("SET search_path TO public;")
                
                # PostgreSQL için SQL syntax - Schema'yı açıkça belirt
                # Stok tablosu
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS public.stok (
                        id SERIAL PRIMARY KEY,
                        urun_kodu VARCHAR(255) UNIQUE,
                        urun_adi VARCHAR(255) NOT NULL,
                        marka VARCHAR(255),
                        birim VARCHAR(50) DEFAULT 'Adet',
                        stok_miktari NUMERIC(10, 2) DEFAULT 0,
                        birim_fiyat NUMERIC(10, 2) DEFAULT 0,
                        aciklama TEXT,
                        olusturma_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        guncelleme_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Cari hesap tablosu
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS public.cari (
                        id SERIAL PRIMARY KEY,
                        cari_kodu VARCHAR(255) UNIQUE,
                        unvan VARCHAR(255) NOT NULL,
                        tip VARCHAR(50) NOT NULL CHECK(tip IN ('Müşteri', 'Tedarikçi')),
                        telefon VARCHAR(50),
                        email VARCHAR(255),
                        adres TEXT,
                        tc_kimlik_no VARCHAR(11) UNIQUE,
                        vergi_no VARCHAR(50),
                        vergi_dairesi VARCHAR(255),
                        bakiye NUMERIC(10, 2) DEFAULT 0,
                        aciklama TEXT,
                        firma_tipi VARCHAR(50) DEFAULT 'Şahıs',
                        olusturma_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        guncelleme_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # İş evrakı tablosu
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS public.is_evraki (
                        id SERIAL PRIMARY KEY,
                        is_emri_no INTEGER NOT NULL,
                        tarih VARCHAR(50) NOT NULL,
                        musteri_unvan VARCHAR(255) NOT NULL,
                        telefon VARCHAR(50),
                        arac_plakasi VARCHAR(20),
                        cekici_dorse VARCHAR(50),
                        marka_model VARCHAR(255),
                        talep_edilen_isler TEXT,
                        musteri_sikayeti TEXT,
                        yapilan_is TEXT,
                        baslama_saati VARCHAR(10),
                        bitis_saati VARCHAR(10),
                        kullanilan_urunler TEXT,
                        toplam_tutar NUMERIC(10, 2) DEFAULT 0,
                        tc_kimlik_no VARCHAR(11),
                        olusturma_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # PostgreSQL için migration (firma_tipi kolonu)
                try:
                    cursor.execute("ALTER TABLE public.cari ADD COLUMN firma_tipi VARCHAR(50) DEFAULT 'Şahıs'")
                    cursor.execute("UPDATE public.cari SET firma_tipi = 'Şahıs' WHERE firma_tipi IS NULL")
                except Exception:
                    pass  # Kolon zaten varsa hata vermez
                
                # Tabloların oluşturulduğunu doğrula
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name IN ('stok', 'cari', 'is_evraki')
                """)
                tables = cursor.fetchall()
                table_names = [row['table_name'] if isinstance(row, dict) else row[0] for row in tables]
                print(f"📊 Oluşturulan tablolar: {', '.join(table_names) if table_names else 'HİÇBİR TABLO BULUNAMADI!'}")
            else:
                # SQLite için SQL syntax
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
                
                # Migration: Eski veritabanları için kolon ekleme (sadece SQLite için)
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
                
                # Migration: firma_tipi kolonu ekle
                try:
                    cursor.execute("ALTER TABLE cari ADD COLUMN firma_tipi TEXT DEFAULT 'Şahıs'")
                    cursor.execute("UPDATE cari SET firma_tipi = 'Şahıs' WHERE firma_tipi IS NULL")
                except sqlite3.OperationalError:
                    pass
            
            conn.commit()
            print("✅ Veritabanı tabloları başarıyla oluşturuldu/doğrulandı")
        except Exception as e:
            # Hata durumunda logla
            print(f"❌ Veritabanı tablo oluşturma hatası: {e}")
            import traceback
            traceback.print_exc()
            try:
                if conn:
                    conn.rollback()
            except:
                pass
            # Hata olsa bile devam et, belki tablolar zaten var
            # Ama exception'ı tekrar fırlat ki startup event'te yakalanabilsin
            raise
        finally:
            # Connection'ı kapatma, çünkü sonraki işlemler için gerekli
            # Sadece cursor'ı kapat
            if cursor:
                try:
                    cursor.close()
                except:
                    pass