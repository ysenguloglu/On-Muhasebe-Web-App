"""
İş prosesi veritabanı işlemleri
"""
from typing import List, Dict, Optional
from .db_connection import DatabaseConnection


class IsProsesiDB:
    """İş prosesi veritabanı işlemleri"""
    
    def __init__(self, db_conn: DatabaseConnection):
        self.db = db_conn
    
    def is_prosesi_ekle(self, proses_adi: str, aciklama: str = "", proses_tipi: Optional[str] = None) -> tuple[bool, str, Optional[int]]:
        """Yeni iş prosesi ekle. proses_tipi: Söküm, Temizlik, Revizyon, Montaj"""
        conn = None
        try:
            conn = self.db.connect()
            cursor = self.db._get_cursor(conn)
            
            aciklama_val = aciklama if aciklama else None
            proses_tipi_val = proses_tipi if proses_tipi else None
            
            query = """
                INSERT INTO is_prosesi (proses_adi, proses_tipi, aciklama)
                VALUES (?, ?, ?)
            """
            query = self.db._convert_placeholders(query)
            cursor.execute(query, (proses_adi, proses_tipi_val, aciklama_val))
            conn.commit()
            
            # Oluşturulan ID'yi al
            proses_id = cursor.lastrowid if hasattr(cursor, 'lastrowid') else None
            if not proses_id and self.db.is_mysql:
                # MySQL için son eklenen ID'yi al
                cursor.execute("SELECT LAST_INSERT_ID()")
                result = cursor.fetchone()
                if result:
                    proses_id = result['LAST_INSERT_ID()'] if isinstance(result, dict) else result[0]
            
            return (True, "İş prosesi başarıyla kaydedildi", proses_id)
        except Exception as e:
            hata_mesaji = f"Veritabanı hatası: {str(e)}"
            print(f"İş prosesi ekleme hatası: {e}")
            if conn:
                try:
                    conn.rollback()
                except:
                    pass
            return (False, hata_mesaji, None)
        finally:
            self.db.close()
    
    def is_prosesi_listele(self) -> List[Dict]:
        """Tüm iş proseslerini listele"""
        conn = self.db.connect()
        cursor = self.db._get_cursor(conn)
        cursor.execute("SELECT * FROM is_prosesi ORDER BY olusturma_tarihi DESC")
        rows = cursor.fetchall()
        self.db.close()
        # MySQL'de DictCursor kullanıldığı için row zaten dict, SQLite'da Row objesi
        if self.db.is_mysql:
            return list(rows)  # Zaten dictionary listesi
        else:
            return [dict(row) for row in rows]  # SQLite Row objesini dict'e çevir
    
    def is_prosesi_getir(self, proses_id: int) -> Optional[Dict]:
        """ID ile iş prosesi getir"""
        conn = self.db.connect()
        cursor = self.db._get_cursor(conn)
        query = "SELECT * FROM is_prosesi WHERE id = ?"
        query = self.db._convert_placeholders(query)
        cursor.execute(query, (proses_id,))
        row = cursor.fetchone()
        self.db.close()
        # MySQL'de DictCursor kullanıldığı için row zaten dict, SQLite'da Row objesi
        if self.db.is_mysql:
            return row if row else None
        else:
            return dict(row) if row else None
    
    def is_prosesi_guncelle(self, proses_id: int, proses_adi: str, aciklama: str = "", proses_tipi: Optional[str] = None) -> tuple[bool, str]:
        """İş prosesi güncelle. proses_tipi: Söküm, Temizlik, Revizyon, Montaj"""
        conn = None
        try:
            conn = self.db.connect()
            cursor = self.db._get_cursor(conn)
            
            # Önce kaydın var olup olmadığını kontrol et
            check_query = "SELECT id FROM is_prosesi WHERE id = ?"
            check_query = self.db._convert_placeholders(check_query)
            cursor.execute(check_query, (proses_id,))
            existing = cursor.fetchone()
            
            if not existing:
                return (False, "İş prosesi bulunamadı")
            
            aciklama_val = aciklama if aciklama else None
            proses_tipi_val = proses_tipi if proses_tipi else None
            
            query = """
                UPDATE is_prosesi 
                SET proses_adi = ?, proses_tipi = ?, aciklama = ?
                WHERE id = ?
            """
            query = self.db._convert_placeholders(query)
            cursor.execute(query, (proses_adi, proses_tipi_val, aciklama_val, proses_id))
            conn.commit()
            
            return (True, "İş prosesi başarıyla güncellendi")
        except Exception as e:
            hata_mesaji = f"Güncelleme hatası: {str(e)}"
            print(f"İş prosesi güncelleme hatası: {e}")
            if conn:
                try:
                    conn.rollback()
                except:
                    pass
            return (False, hata_mesaji)
        finally:
            self.db.close()
    
    def is_prosesi_sil(self, proses_id: int) -> tuple[bool, str]:
        """İş prosesi sil (maddeleri de otomatik silinir - CASCADE)"""
        conn = None
        try:
            conn = self.db.connect()
            cursor = self.db._get_cursor(conn)
            query = "DELETE FROM is_prosesi WHERE id = ?"
            query = self.db._convert_placeholders(query)
            cursor.execute(query, (proses_id,))
            conn.commit()
            
            if cursor.rowcount == 0:
                return (False, "İş prosesi bulunamadı")
            
            return (True, "İş prosesi başarıyla silindi")
        except Exception as e:
            hata_mesaji = f"Silme hatası: {str(e)}"
            print(f"İş prosesi silme hatası: {e}")
            if conn:
                try:
                    conn.rollback()
                except:
                    pass
            return (False, hata_mesaji)
        finally:
            self.db.close()
    
    # ========== PROSES MADDELERİ İŞLEMLERİ ==========
    
    def is_prosesi_madde_ekle(self, proses_id: int, sira_no: int, madde_adi: str, aciklama: str = "") -> tuple[bool, str, Optional[int]]:
        """Yeni proses maddesi ekle"""
        conn = None
        try:
            conn = self.db.connect()
            cursor = self.db._get_cursor(conn)
            
            aciklama_val = aciklama if aciklama else None
            
            query = """
                INSERT INTO is_prosesi_maddeleri (proses_id, sira_no, madde_adi, aciklama)
                VALUES (?, ?, ?, ?)
            """
            query = self.db._convert_placeholders(query)
            cursor.execute(query, (proses_id, sira_no, madde_adi, aciklama_val))
            conn.commit()
            
            # Oluşturulan ID'yi al
            madde_id = cursor.lastrowid if hasattr(cursor, 'lastrowid') else None
            if not madde_id and self.db.is_mysql:
                cursor.execute("SELECT LAST_INSERT_ID()")
                result = cursor.fetchone()
                if result:
                    madde_id = result['LAST_INSERT_ID()'] if isinstance(result, dict) else result[0]
            
            return (True, "Proses maddesi başarıyla kaydedildi", madde_id)
        except Exception as e:
            hata_mesaji = f"Veritabanı hatası: {str(e)}"
            print(f"Proses maddesi ekleme hatası: {e}")
            if conn:
                try:
                    conn.rollback()
                except:
                    pass
            return (False, hata_mesaji, None)
        finally:
            self.db.close()
    
    def is_prosesi_maddeleri_getir(self, proses_id: int) -> List[Dict]:
        """Proses maddelerini getir"""
        conn = self.db.connect()
        cursor = self.db._get_cursor(conn)
        query = "SELECT * FROM is_prosesi_maddeleri WHERE proses_id = ? ORDER BY sira_no ASC"
        query = self.db._convert_placeholders(query)
        cursor.execute(query, (proses_id,))
        rows = cursor.fetchall()
        self.db.close()
        # MySQL'de DictCursor kullanıldığı için row zaten dict, SQLite'da Row objesi
        if self.db.is_mysql:
            return list(rows)  # Zaten dictionary listesi
        else:
            return [dict(row) for row in rows]  # SQLite Row objesini dict'e çevir
    
    def is_prosesi_madde_guncelle(self, madde_id: int, sira_no: int, madde_adi: str, 
                                   aciklama: str = "", tamamlandi: bool = False) -> tuple[bool, str]:
        """Proses maddesi güncelle"""
        conn = None
        try:
            conn = self.db.connect()
            cursor = self.db._get_cursor(conn)
            
            # Önce kaydın var olup olmadığını kontrol et
            check_query = "SELECT id FROM is_prosesi_maddeleri WHERE id = ?"
            check_query = self.db._convert_placeholders(check_query)
            cursor.execute(check_query, (madde_id,))
            existing = cursor.fetchone()
            
            if not existing:
                return (False, "Proses maddesi bulunamadı")
            
            aciklama_val = aciklama if aciklama else None
            
            # Tamamlanma tarihi
            if tamamlandi:
                if self.db.is_mysql:
                    tamamlanma_tarihi = "CURRENT_TIMESTAMP"
                else:
                    tamamlanma_tarihi = "datetime('now')"
            else:
                tamamlanma_tarihi = None
            
            # Boolean değeri dönüştür (SQLite için 0/1, MySQL için True/False)
            tamamlandi_val = 1 if tamamlandi else 0 if not self.db.is_mysql else tamamlandi
            
            if tamamlanma_tarihi:
                query = """
                    UPDATE is_prosesi_maddeleri 
                    SET sira_no = ?, madde_adi = ?, aciklama = ?, tamamlandi = ?, tamamlanma_tarihi = {}
                    WHERE id = ?
                """.format(tamamlanma_tarihi)
            else:
                query = """
                    UPDATE is_prosesi_maddeleri 
                    SET sira_no = ?, madde_adi = ?, aciklama = ?, tamamlandi = ?, tamamlanma_tarihi = NULL
                    WHERE id = ?
                """
            query = self.db._convert_placeholders(query)
            cursor.execute(query, (sira_no, madde_adi, aciklama_val, tamamlandi_val, madde_id))
            conn.commit()
            
            return (True, "Proses maddesi başarıyla güncellendi")
        except Exception as e:
            hata_mesaji = f"Güncelleme hatası: {str(e)}"
            print(f"Proses maddesi güncelleme hatası: {e}")
            if conn:
                try:
                    conn.rollback()
                except:
                    pass
            return (False, hata_mesaji)
        finally:
            self.db.close()
    
    def is_prosesi_madde_sil(self, madde_id: int) -> tuple[bool, str]:
        """Proses maddesi sil"""
        conn = None
        try:
            conn = self.db.connect()
            cursor = self.db._get_cursor(conn)
            query = "DELETE FROM is_prosesi_maddeleri WHERE id = ?"
            query = self.db._convert_placeholders(query)
            cursor.execute(query, (madde_id,))
            conn.commit()
            
            if cursor.rowcount == 0:
                return (False, "Proses maddesi bulunamadı")
            
            return (True, "Proses maddesi başarıyla silindi")
        except Exception as e:
            hata_mesaji = f"Silme hatası: {str(e)}"
            print(f"Proses maddesi silme hatası: {e}")
            if conn:
                try:
                    conn.rollback()
                except:
                    pass
            return (False, hata_mesaji)
        finally:
            self.db.close()
    
    def is_prosesi_tamamla_madde(self, madde_id: int, tamamlandi: bool = True) -> tuple[bool, str]:
        """Proses maddesini tamamlandı olarak işaretle"""
        conn = None
        try:
            conn = self.db.connect()
            cursor = self.db._get_cursor(conn)
            
            # Boolean değeri dönüştür
            tamamlandi_val = 1 if tamamlandi else 0 if not self.db.is_mysql else tamamlandi
            
            if tamamlandi:
                if self.db.is_mysql:
                    query = """
                        UPDATE is_prosesi_maddeleri 
                        SET tamamlandi = ?, tamamlanma_tarihi = CURRENT_TIMESTAMP
                        WHERE id = ?
                    """
                else:
                    query = """
                        UPDATE is_prosesi_maddeleri 
                        SET tamamlandi = ?, tamamlanma_tarihi = datetime('now')
                        WHERE id = ?
                    """
            else:
                query = """
                    UPDATE is_prosesi_maddeleri 
                    SET tamamlandi = ?, tamamlanma_tarihi = NULL
                    WHERE id = ?
                """
            query = self.db._convert_placeholders(query)
            cursor.execute(query, (tamamlandi_val, madde_id))
            conn.commit()
            
            return (True, "Proses maddesi durumu güncellendi")
        except Exception as e:
            hata_mesaji = f"Güncelleme hatası: {str(e)}"
            print(f"Proses maddesi tamamlama hatası: {e}")
            if conn:
                try:
                    conn.rollback()
                except:
                    pass
            return (False, hata_mesaji)
        finally:
            self.db.close()
