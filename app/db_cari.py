"""
Cari hesap veritabanı işlemleri
"""
from typing import Optional, List, Dict
from .db_connection import DatabaseConnection


class CariDB:
    """Cari hesap veritabanı işlemleri"""
    
    def __init__(self, db_conn: DatabaseConnection):
        self.db = db_conn
    
    def cari_ekle(self, cari_kodu: str, unvan: str, tip: str, 
                  telefon: str = "", email: str = "", adres: str = "",
                  tc_kimlik_no: str = "", vergi_no: str = "", vergi_dairesi: str = "", 
                  bakiye: float = 0, aciklama: str = "", firma_tipi: str = "Şahıs") -> bool:
        """Yeni cari hesap ekle"""
        conn = None
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            cari_kodu_val = cari_kodu.strip() if cari_kodu and cari_kodu.strip() else None
            tc_kimlik_no_val = tc_kimlik_no.strip() if tc_kimlik_no and tc_kimlik_no.strip() else None
            vergi_no_val = vergi_no.strip() if vergi_no and vergi_no.strip() else None
            bakiye_val = float(bakiye) if bakiye is not None else 0.0
            query = """
                INSERT INTO cari (cari_kodu, unvan, tip, telefon, email, adres,
                                tc_kimlik_no, vergi_no, vergi_dairesi, bakiye, aciklama, firma_tipi)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            query = self.db._convert_placeholders(query)
            cursor.execute(query, (cari_kodu_val, unvan, tip, telefon, email, adres, 
                  tc_kimlik_no_val, vergi_no_val, vergi_dairesi, bakiye_val, aciklama, firma_tipi))
            conn.commit()
            return True
        except Exception as e:
            if self.db._is_integrity_error(e):
                if conn:
                    try:
                        conn.rollback()
                    except:
                        pass
                return False
            print(f"Cari ekleme hatası: {e}")
            if conn:
                try:
                    conn.rollback()
                except:
                    pass
            return False
        finally:
            self.db.close()
    
    def cari_guncelle(self, cari_id: int, cari_kodu: str, unvan: str, tip: str,
                     telefon: str, email: str, adres: str, vergi_no: str,
                     vergi_dairesi: str, bakiye: float, aciklama: str, firma_tipi: str = "Şahıs") -> bool:
        """Cari hesap bilgilerini güncelle"""
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            cari_kodu_val = cari_kodu if cari_kodu else None
            query = """
                UPDATE cari 
                SET cari_kodu = ?, unvan = ?, tip = ?, telefon = ?, email = ?,
                    adres = ?, vergi_no = ?, vergi_dairesi = ?, bakiye = ?,
                    aciklama = ?, firma_tipi = ?, guncelleme_tarihi = CURRENT_TIMESTAMP
                WHERE id = ?
            """
            query = self.db._convert_placeholders(query)
            cursor.execute(query, (cari_kodu_val, unvan, tip, telefon, email, adres, vergi_no,
                  vergi_dairesi, bakiye, aciklama, firma_tipi, cari_id))
            conn.commit()
            self.db.close()
            return True
        except Exception as e:
            if self.db._is_integrity_error(e):
                return False
            print(f"Cari güncelleme hatası: {e}")
            return False
    
    def cari_sil(self, cari_id: int) -> bool:
        """Cari hesabı sil"""
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            query = "DELETE FROM cari WHERE id = ?"
            query = self.db._convert_placeholders(query)
            cursor.execute(query, (cari_id,))
            conn.commit()
            self.db.close()
            return True
        except Exception as e:
            print(f"Cari silme hatası: {e}")
            return False
    
    def cari_listele(self, arama: str = "", tip: str = "") -> List[Dict]:
        """Tüm cari hesapları listele"""
        conn = self.db.connect()
        cursor = conn.cursor()
        
        query = "SELECT * FROM cari WHERE 1=1"
        params = []
        
        if arama:
            query += " AND (cari_kodu LIKE ? OR unvan LIKE ?)"
            params.extend([f"%{arama}%", f"%{arama}%"])
        
        if tip:
            query += " AND tip = ?"
            params.append(tip)
        
        query += " ORDER BY unvan"
        query = self.db._convert_placeholders(query)
        cursor.execute(query, params)
        rows = cursor.fetchall()
        self.db.close()
        return [dict(row) for row in rows]
    
    def cari_getir(self, cari_id: int) -> Optional[Dict]:
        """Belirli bir cari hesabı getir"""
        conn = self.db.connect()
        cursor = conn.cursor()
        query = "SELECT * FROM cari WHERE id = ?"
        query = self.db._convert_placeholders(query)
        cursor.execute(query, (cari_id,))
        row = cursor.fetchone()
        self.db.close()
        return dict(row) if row else None
    
    def cari_tc_ile_ara(self, tc_kimlik_no: str) -> Optional[Dict]:
        """TC kimlik no ile cari hesap ara"""
        if not tc_kimlik_no or not tc_kimlik_no.strip():
            return None
        conn = None
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            query = "SELECT * FROM cari WHERE tc_kimlik_no = ?"
            query = self.db._convert_placeholders(query)
            cursor.execute(query, (tc_kimlik_no.strip(),))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            if conn:
                try:
                    conn.close()
                    self.db.conn = None
                except:
                    pass
    
    def cari_unvan_ile_ara(self, unvan: str) -> Optional[Dict]:
        """Ünvan ile cari hesap ara"""
        if not unvan or not unvan.strip():
            return None
        conn = None
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            query = "SELECT * FROM cari WHERE unvan = ?"
            query = self.db._convert_placeholders(query)
            cursor.execute(query, (unvan.strip(),))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            if conn:
                try:
                    conn.close()
                    self.db.conn = None
                except:
                    pass
    
    def cari_sonraki_kod_olustur(self) -> str:
        """Bir sonraki cari kodunu oluştur (sayısal)"""
        conn = None
        try:
            conn = self.db.connect()
            # PostgreSQL için RealDictCursor, SQLite için normal cursor
            if self.db.is_postgres:
                from psycopg2.extras import RealDictCursor
                cursor = conn.cursor(cursor_factory=RealDictCursor)
            else:
                cursor = conn.cursor()
            
            if self.db.is_postgres:
                # PostgreSQL için ~ (regex) operatörü kullan
                query = """
                    SELECT cari_kodu FROM cari 
                    WHERE cari_kodu IS NOT NULL 
                    AND cari_kodu ~ '^[0-9]+$'
                    ORDER BY CAST(cari_kodu AS INTEGER) DESC
                    LIMIT 1
                """
            else:
                # SQLite için GLOB kullan
                query = """
                    SELECT cari_kodu FROM cari 
                    WHERE cari_kodu IS NOT NULL 
                    AND cari_kodu GLOB '[0-9]*'
                    ORDER BY CAST(cari_kodu AS INTEGER) DESC
                    LIMIT 1
                """
            cursor.execute(query)
            row = cursor.fetchone()
            
            # PostgreSQL ve SQLite için farklı erişim
            if row:
                if self.db.is_postgres:
                    cari_kodu = row['cari_kodu']
                else:
                    cari_kodu = row[0]
                
                if cari_kodu:
                    try:
                        son_kod = int(cari_kodu)
                        return str(son_kod + 1)
                    except ValueError:
                        pass
            return "1"
        finally:
            if conn:
                try:
                    conn.close()
                    self.db.conn = None
                except:
                    pass
    
    def cari_ekle_tc_kontrolu_ile(self, cari_kodu: str, unvan: str, tip: str,
                                  telefon: str = "", email: str = "", adres: str = "",
                                  tc_kimlik_no: str = "", vergi_no: str = "", 
                                  vergi_dairesi: str = "", bakiye: float = 0, 
                                  aciklama: str = "", firma_tipi: str = "Şahıs") -> tuple[bool, str]:
        """TC ve VKN kontrolü yaparak cari hesap ekle"""
        # TC kimlik no kontrolü
        if tc_kimlik_no and tc_kimlik_no.strip():
            mevcut_cari = self.cari_tc_ile_ara(tc_kimlik_no)
            if mevcut_cari:
                return (True, f"Bu TC kimlik no'ya sahip cari hesap zaten mevcut: {mevcut_cari.get('unvan', '')}")
        
        # VKN (vergi_no) kontrolü
        if vergi_no and vergi_no.strip():
            conn = None
            try:
                conn = self.db.connect()
                cursor = conn.cursor()
                query = "SELECT * FROM cari WHERE vergi_no = ?"
                query = self.db._convert_placeholders(query)
                cursor.execute(query, (vergi_no.strip(),))
                row = cursor.fetchone()
                if row:
                    mevcut_cari = dict(row)
                    return (True, f"Bu VKN'ye sahip cari hesap zaten mevcut: {mevcut_cari.get('unvan', '')}")
            finally:
                if conn:
                    try:
                        conn.close()
                        self.db.conn = None
                    except:
                        pass
        
        if not tc_kimlik_no or not tc_kimlik_no.strip():
            mevcut_cari = self.cari_unvan_ile_ara(unvan)
            if mevcut_cari:
                if not mevcut_cari.get('tc_kimlik_no'):
                    if tc_kimlik_no and tc_kimlik_no.strip():
                        conn = None
                        try:
                            conn = self.db.connect()
                            cursor = conn.cursor()
                            query = "UPDATE cari SET tc_kimlik_no = ? WHERE id = ?"
                            query = self.db._convert_placeholders(query)
                            cursor.execute(query, (tc_kimlik_no.strip(), mevcut_cari['id']))
                            conn.commit()
                        except Exception as e:
                            print(f"TC güncelleme hatası: {e}")
                            if conn:
                                try:
                                    conn.rollback()
                                except:
                                    pass
                        finally:
                            if conn:
                                try:
                                    conn.close()
                                    self.db.conn = None
                                except:
                                    pass
                return (True, f"Aynı ünvana sahip cari hesap zaten mevcut: {unvan}")
        
        if not cari_kodu or not cari_kodu.strip():
            cari_kodu = self.cari_sonraki_kod_olustur()
        
        if tc_kimlik_no and tc_kimlik_no.strip() and not vergi_no:
            vergi_no = tc_kimlik_no.strip()
        
        conn = None
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            query = "SELECT id FROM cari WHERE cari_kodu = ?"
            query = self.db._convert_placeholders(query)
            cursor.execute(query, (cari_kodu,))
            if cursor.fetchone():
                cari_kodu = self.cari_sonraki_kod_olustur()
                query = "SELECT id FROM cari WHERE cari_kodu = ?"
                query = self.db._convert_placeholders(query)
                cursor.execute(query, (cari_kodu,))
                sayac = 0
                while cursor.fetchone() and sayac < 100:
                    cari_kodu = str(int(cari_kodu) + 1)
                    query = "SELECT id FROM cari WHERE cari_kodu = ?"
                    query = self.db._convert_placeholders(query)
                    cursor.execute(query, (cari_kodu,))
                    sayac += 1
        finally:
            if conn:
                try:
                    conn.close()
                    self.db.conn = None
                except:
                    pass
        
        if self.cari_ekle(cari_kodu, unvan, tip, telefon, email, adres,
                         tc_kimlik_no, vergi_no, vergi_dairesi, bakiye, aciklama, firma_tipi):
            return (True, f"Cari hesap başarıyla eklendi (Cari Kodu: {cari_kodu})")
        else:
            mevcut_cari = self.cari_unvan_ile_ara(unvan)
            if mevcut_cari:
                return (True, f"Aynı ünvana sahip cari hesap zaten mevcut: {unvan}")
            return (False, "Cari hesap eklenirken bir hata oluştu")

