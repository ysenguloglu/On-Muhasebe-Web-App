"""
Veritabanı bağlantı yönetimi - MySQL
"""
import os
from typing import Optional
from dotenv import load_dotenv
from urllib.parse import urlparse

import pymysql
from pymysql.cursors import DictCursor

load_dotenv()


class DatabaseConnection:
    """Veritabanı bağlantı yönetimi - yalnızca MySQL"""

    def __init__(self, database_url: Optional[str] = None):
        """
        MySQL bağlantısı. database_url zorunludur.
        Format: mysql://user:password@host:port/database veya mysql+pymysql://...
        """
        self.database_url = database_url or os.getenv("DATABASE_URL")
        self.conn = None

        if not self.database_url or not (
            self.database_url.startswith("mysql://")
            or self.database_url.startswith("mysql+pymysql://")
        ):
            raise ValueError(
                "DATABASE_URL (MySQL) gerekli. Örnek: mysql://user:password@host:3306/dbadi"
            )

    def _parse_mysql_url(self, url: str) -> dict:
        """MySQL URL'ini parse et"""
        if url.startswith("mysql+pymysql://"):
            url = url.replace("mysql+pymysql://", "mysql://", 1)
        parsed = urlparse(url)
        return {
            "host": parsed.hostname or "localhost",
            "port": parsed.port or 3306,
            "user": parsed.username or "root",
            "password": parsed.password or "",
            "database": parsed.path.lstrip("/") if parsed.path else None,
            "charset": "utf8mb4",
        }

    def connect(self):
        """MySQL bağlantısı oluştur"""
        if self.conn:
            try:
                self.conn.close()
            except Exception:
                pass
            finally:
                self.conn = None

        config = self._parse_mysql_url(self.database_url)
        self.conn = pymysql.connect(**config)
        return self.conn

    def close(self):
        """Bağlantıyı kapat"""
        if self.conn:
            try:
                self.conn.close()
            except Exception:
                pass
            finally:
                self.conn = None

    def _get_cursor(self, conn=None):
        """DictCursor oluştur"""
        if conn is None:
            conn = self.connect()
        return conn.cursor(DictCursor)

    def _convert_placeholders(self, query: str) -> str:
        """? -> %s (MySQL)"""
        return query.replace("?", "%s")

    def _is_integrity_error(self, exception: Exception) -> bool:
        """pymysql IntegrityError / OperationalError"""
        try:
            import pymysql.err

            return isinstance(
                exception, (pymysql.err.IntegrityError, pymysql.err.OperationalError)
            )
        except Exception:
            s = str(exception).lower()
            return "duplicate" in s or "integrity" in s or "unique" in s

    def init_database(self):
        """Tabloları oluştur / güncelle (MySQL)"""
        conn = None
        cursor = None
        try:
            conn = self.connect()
            cursor = conn.cursor()

            try:
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
                print(f"⚠️ Stok tablosu (devam): {e}")

            try:
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
                print(f"⚠️ Cari tablosu (devam): {e}")

            try:
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
                print(f"⚠️ İş evrakı tablosu (devam): {e}")

            try:
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
                print(f"⚠️ İş prosesi tablosu (devam): {e}")

            try:
                cursor.execute("ALTER TABLE is_prosesi ADD COLUMN proses_tipi VARCHAR(50) NULL")
                conn.commit()
            except Exception:
                conn.rollback()

            try:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS is_prosesi_maddeleri (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        proses_id INT NOT NULL,
                        sira_no INT NOT NULL,
                        madde_adi VARCHAR(255) NOT NULL,
                        aciklama TEXT,
                        kullanilan_malzemeler TEXT,
                        tamamlandi BOOLEAN DEFAULT FALSE,
                        tamamlanma_tarihi TIMESTAMP NULL,
                        olusturma_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (proses_id) REFERENCES is_prosesi(id) ON DELETE CASCADE
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """)
                conn.commit()
            except Exception as e:
                conn.rollback()
                print(f"⚠️ İş prosesi maddeleri (devam): {e}")

            # kullanilan_malzemeler kolonunu ekle (eğer yoksa)
            try:
                cursor.execute("ALTER TABLE is_prosesi_maddeleri ADD COLUMN kullanilan_malzemeler TEXT")
                conn.commit()
            except Exception:
                conn.rollback()
                # Kolon zaten varsa hata vermez, devam eder

            try:
                cursor.execute("ALTER TABLE cari ADD COLUMN firma_tipi VARCHAR(50) DEFAULT 'Şahıs'")
                cursor.execute("UPDATE cari SET firma_tipi = 'Şahıs' WHERE firma_tipi IS NULL")
                conn.commit()
            except Exception:
                conn.rollback()

            try:
                cursor.execute("""
                    SELECT table_name FROM information_schema.tables
                    WHERE table_schema = DATABASE()
                    AND table_name IN ('stok', 'cari', 'is_evraki', 'is_prosesi', 'is_prosesi_maddeleri')
                """)
                rows = cursor.fetchall()
                names = [r[0] for r in rows] if rows else []
                print(f"📊 Tablolar: {', '.join(names) if names else '-'}")
            except Exception as e:
                print(f"⚠️ Tablo kontrolü: {e}")

            conn.commit()
            print("✅ Veritabanı (MySQL) hazır")
        except Exception as e:
            print(f"❌ Veritabanı hatası: {e}")
            import traceback
            traceback.print_exc()
            if conn:
                try:
                    conn.rollback()
                except Exception:
                    pass
            raise
        finally:
            if cursor:
                try:
                    cursor.close()
                except Exception:
                    pass
