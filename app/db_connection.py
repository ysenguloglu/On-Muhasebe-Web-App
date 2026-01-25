"""
Veritabanı bağlantı yönetimi
SQLite ve MySQL veritabanı bağlantı işlemleri
"""
import os
import sqlite3
from typing import Optional
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()

# MySQL için pymysql import (opsiyonel)
try:
    import pymysql
    from pymysql.cursors import DictCursor
    PYMySQL_AVAILABLE = True
except ImportError:
    PYMySQL_AVAILABLE = False


class DatabaseConnection:
    """Veritabanı bağlantı yönetim sınıfı - SQLite ve MySQL desteği"""
    
    def __init__(self, db_path: Optional[str] = None, database_url: Optional[str] = None):
        """
        Veritabanı bağlantısı oluştur
        
        Args:
            db_path: SQLite veritabanı dosya yolu (SQLite için)
            database_url: MySQL connection string (MySQL için)
        """
        self.database_url = database_url or os.getenv("DATABASE_URL")
        self.db_path = db_path or "on_muhasebe.db"
        self.conn = None
        self.is_mysql = False
        
        # DATABASE_URL varsa MySQL kullan
        # MySQL URL formatı: mysql://user:password@host:port/database
        if self.database_url and (self.database_url.startswith("mysql://") or self.database_url.startswith("mysql+pymysql://")):
            self.is_mysql = True
            if not PYMySQL_AVAILABLE:
                raise ImportError("MySQL kullanmak için pymysql paketi yüklü olmalı")
    
    def _parse_mysql_url(self, url: str) -> dict:
        """MySQL URL'ini parse et"""
        # mysql:// veya mysql+pymysql:// formatını destekle
        if url.startswith("mysql+pymysql://"):
            url = url.replace("mysql+pymysql://", "mysql://", 1)
        
        parsed = urlparse(url)
        return {
            'host': parsed.hostname or 'localhost',
            'port': parsed.port or 3306,
            'user': parsed.username or 'root',
            'password': parsed.password or '',
            'database': parsed.path.lstrip('/') if parsed.path else None,
            'charset': 'utf8mb4'
        }
    
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
        
        if self.is_mysql:
            # MySQL bağlantısı
            config = self._parse_mysql_url(self.database_url)
            self.conn = pymysql.connect(**config)
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
    
    def _get_cursor(self, conn=None):
        """Cursor oluştur - MySQL için DictCursor, SQLite için normal cursor
        Eğer conn parametresi verilmişse onu kullan, yoksa yeni connection oluştur"""
        if conn is None:
            conn = self.connect()
        if self.is_mysql:
            return conn.cursor(DictCursor)
        else:
            return conn.cursor()
    
    def _convert_placeholders(self, query: str) -> str:
        """Placeholder'ları veritabanı tipine göre dönüştür (? -> %s MySQL için)"""
        if self.is_mysql:
            # MySQL için ? -> %s
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
        if self.is_mysql:
            # MySQL için pymysql.err.IntegrityError
            try:
                import pymysql.err
                return isinstance(exception, (pymysql.err.IntegrityError, pymysql.err.OperationalError))
            except:
                # Eğer pymysql.err import edilemezse, exception tipine bak
                return 'duplicate' in str(exception).lower() or 'integrity' in str(exception).lower() or 'unique' in str(exception).lower()
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
            
            if self.is_mysql:
                # MySQL için SQL syntax - SQLite'daki gibi TEXT kullan
                # Her tablo için ayrı transaction kullan
                try:
                    # Stok tablosu
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS stok (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            urun_kodu VARCHAR(255) UNIQUE,
                            urun_adi VARCHAR(255) NOT NULL,
                            marka VARCHAR(255),
                            birim VARCHAR(50) DEFAULT 'Adet',
                            stok_miktari DECIMAL(10, 2) DEFAULT 0,
                            birim_fiyat DECIMAL(10, 2) DEFAULT 0,
                            aciklama TEXT,
                            olusturma_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            guncelleme_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                    """)
                    conn.commit()
                except Exception as e:
                    conn.rollback()
                    print(f"⚠️ Stok tablosu oluşturma hatası (devam ediliyor): {e}")
                
                try:
                    # Cari hesap tablosu
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS cari (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            cari_kodu VARCHAR(255) UNIQUE,
                            unvan VARCHAR(255) NOT NULL,
                            tip VARCHAR(50) NOT NULL CHECK(tip IN ('Müşteri', 'Tedarikçi')),
                            telefon VARCHAR(50),
                            email VARCHAR(255),
                            adres TEXT,
                            tc_kimlik_no VARCHAR(11) UNIQUE,
                            vergi_no VARCHAR(50),
                            vergi_dairesi VARCHAR(255),
                            bakiye DECIMAL(10, 2) DEFAULT 0,
                            aciklama TEXT,
                            firma_tipi VARCHAR(50) DEFAULT 'Şahıs',
                            olusturma_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            guncelleme_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                    """)
                    conn.commit()
                except Exception as e:
                    conn.rollback()
                    print(f"⚠️ Cari tablosu oluşturma hatası (devam ediliyor): {e}")
                
                try:
                    # İş evrakı tablosu
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS is_evraki (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            is_emri_no INT NOT NULL,
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
                            toplam_tutar DECIMAL(10, 2) DEFAULT 0,
                            tc_kimlik_no VARCHAR(11),
                            olusturma_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                    """)
                    conn.commit()
                except Exception as e:
                    conn.rollback()
                    print(f"⚠️ İş evrakı tablosu oluşturma hatası (devam ediliyor): {e}")
                
                try:
                    # İş prosesi tablosu
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS is_prosesi (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            proses_adi VARCHAR(255) NOT NULL,
                            proses_tipi VARCHAR(50) NULL,
                            aciklama TEXT,
                            olusturma_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            guncelleme_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                    """)
                    conn.commit()
                except Exception as e:
                    conn.rollback()
                    print(f"⚠️ İş prosesi tablosu oluşturma hatası (devam ediliyor): {e}")

                # Migration: is_prosesi.proses_tipi (Söküm, Temizlik, Revizyon, Montaj)
                try:
                    cursor.execute("ALTER TABLE is_prosesi ADD COLUMN proses_tipi VARCHAR(50) NULL")
                    conn.commit()
                except Exception:
                    conn.rollback()
                    pass
                
                try:
                    # İş prosesi maddeleri tablosu
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS is_prosesi_maddeleri (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            proses_id INT NOT NULL,
                            sira_no INT NOT NULL,
                            madde_adi VARCHAR(255) NOT NULL,
                            aciklama TEXT,
                            tamamlandi BOOLEAN DEFAULT FALSE,
                            tamamlanma_tarihi TIMESTAMP NULL,
                            olusturma_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (proses_id) REFERENCES is_prosesi(id) ON DELETE CASCADE
                        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                    """)
                    conn.commit()
                except Exception as e:
                    conn.rollback()
                    print(f"⚠️ İş prosesi maddeleri tablosu oluşturma hatası (devam ediliyor): {e}")
                
                # MySQL için migration (firma_tipi kolonu)
                try:
                    cursor.execute("ALTER TABLE cari ADD COLUMN firma_tipi VARCHAR(50) DEFAULT 'Şahıs'")
                    cursor.execute("UPDATE cari SET firma_tipi = 'Şahıs' WHERE firma_tipi IS NULL")
                    conn.commit()
                except Exception:
                    conn.rollback()
                    pass  # Kolon zaten varsa hata vermez
                
                # Tabloların oluşturulduğunu doğrula (yeni transaction)
                try:
                    cursor.execute("""
                        SELECT table_name 
                        FROM information_schema.tables 
                        WHERE table_schema = DATABASE()
                        AND table_name IN ('stok', 'cari', 'is_evraki', 'is_prosesi', 'is_prosesi_maddeleri')
                    """)
                    tables = cursor.fetchall()
                    table_names = [row['table_name'] if isinstance(row, dict) else row[0] for row in tables]
                    print(f"📊 Oluşturulan tablolar: {', '.join(table_names) if table_names else 'HİÇBİR TABLO BULUNAMADI!'}")
                except Exception as e:
                    print(f"⚠️ Tablo kontrolü hatası: {e}")
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
                
                # İş prosesi tablosu
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS is_prosesi (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        proses_adi TEXT NOT NULL,
                        proses_tipi TEXT,
                        aciklama TEXT,
                        olusturma_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        guncelleme_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # İş prosesi maddeleri tablosu
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS is_prosesi_maddeleri (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        proses_id INTEGER NOT NULL,
                        sira_no INTEGER NOT NULL,
                        madde_adi TEXT NOT NULL,
                        aciklama TEXT,
                        tamamlandi INTEGER DEFAULT 0,
                        tamamlanma_tarihi TIMESTAMP,
                        olusturma_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (proses_id) REFERENCES is_prosesi(id) ON DELETE CASCADE
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

                # Migration: is_prosesi.proses_tipi (Söküm, Temizlik, Revizyon, Montaj)
                try:
                    cursor.execute("ALTER TABLE is_prosesi ADD COLUMN proses_tipi TEXT")
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
