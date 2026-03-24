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
                        odeme_durumu VARCHAR(20) DEFAULT 'odenmedi',
                        olusturma_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """)
                conn.commit()
            except Exception as e:
                conn.rollback()
                print(f"⚠️ İş evrakı tablosu (devam): {e}")
            try:
                cursor.execute("ALTER TABLE is_evraki ADD COLUMN odeme_durumu VARCHAR(20) DEFAULT 'odenmedi'")
                conn.commit()
            except Exception:
                conn.rollback()

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

            # Kullanıcılar tablosu (roller: admin, user, operasyon_yoneticisi, sofor, servis_teknisyeni)
            try:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        username VARCHAR(100) NOT NULL UNIQUE,
                        password_hash VARCHAR(255) NOT NULL,
                        role VARCHAR(30) NOT NULL DEFAULT 'user',
                        olusturma_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """)
                conn.commit()
            except Exception as e:
                conn.rollback()
                print(f"⚠️ Users tablosu (devam): {e}")

            # Araç Yönetimi (Modül 2): arac, arac_belge, arac_bakim
            try:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS arac (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        arac_plakasi VARCHAR(20) NOT NULL UNIQUE,
                        arac_tipi VARCHAR(20) NOT NULL DEFAULT 'diğer',
                        marka VARCHAR(100),
                        model VARCHAR(100),
                        model_yili INT,
                        sasi_no VARCHAR(17),
                        motor_no VARCHAR(100),
                        guncel_km DECIMAL(12, 2) DEFAULT 0,
                        alis_tarihi DATE,
                        alis_fiyati DECIMAL(12, 2),
                        durum VARCHAR(20) NOT NULL DEFAULT 'aktif',
                        olusturma_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        guncelleme_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """)
                conn.commit()
            except Exception as e:
                conn.rollback()
                print(f"⚠️ arac tablosu (devam): {e}")

            try:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS arac_belge (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        arac_id INT NOT NULL,
                        belge_turu VARCHAR(50) NOT NULL,
                        duzenlenme_tarihi DATE,
                        bitis_tarihi DATE NOT NULL,
                        belge_dosya_path VARCHAR(500),
                        kayit_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (arac_id) REFERENCES arac(id) ON DELETE CASCADE
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """)
                conn.commit()
            except Exception as e:
                conn.rollback()
                print(f"⚠️ arac_belge tablosu (devam): {e}")

            try:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS arac_bakim (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        arac_id INT NOT NULL,
                        bakim_turu VARCHAR(50) NOT NULL,
                        aciklama TEXT,
                        bakim_tarihi DATE NOT NULL,
                        bakim_km DECIMAL(12, 2),
                        maliyet DECIMAL(12, 2),
                        kayit_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (arac_id) REFERENCES arac(id) ON DELETE CASCADE
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """)
                conn.commit()
            except Exception as e:
                conn.rollback()
                print(f"⚠️ arac_bakim tablosu (devam): {e}")

            try:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS sofor (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        ad_soyad VARCHAR(255) NOT NULL,
                        tc_kimlik_no VARCHAR(11) NOT NULL UNIQUE,
                        telefon VARCHAR(50) NOT NULL,
                        email VARCHAR(255),
                        adres TEXT,
                        ise_baslama_tarihi DATE NOT NULL,
                        src_belge_no VARCHAR(100) NOT NULL,
                        src_bitis_tarihi DATE NOT NULL,
                        ehliyet_sinifi VARCHAR(30) NOT NULL,
                        ehliyet_bitis_tarihi DATE NOT NULL,
                        psikoteknik_bitis DATE NOT NULL,
                        acil_iletisim VARCHAR(255) NOT NULL,
                        iban VARCHAR(34),
                        durum VARCHAR(20) NOT NULL DEFAULT 'aktif',
                        olusturma_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        guncelleme_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """)
                conn.commit()
            except Exception as e:
                conn.rollback()
                print(f"⚠️ sofor tablosu (devam): {e}")

            try:
                cursor.execute("""
                    SELECT table_name FROM information_schema.tables
                    WHERE table_schema = DATABASE()
                    AND table_name IN ('stok', 'cari', 'is_evraki', 'is_prosesi', 'is_prosesi_maddeleri', 'users', 'arac', 'arac_belge', 'arac_bakim', 'sofor')
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
