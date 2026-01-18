"""
Stok veritabanı işlemleri
"""
import sqlite3
from typing import Optional, List, Dict, Tuple, Any
from .db_connection import DatabaseConnection


class StokDB:
    """Stok veritabanı işlemleri"""
    
    def __init__(self, db_conn: DatabaseConnection):
        self.db = db_conn
    
    def stok_ekle(self, urun_kodu: str, urun_adi: str, marka: str = "", 
                  birim: str = "Adet", stok_miktari: float = 0, 
                  birim_fiyat: float = 0, aciklama: str = "") -> bool:
        """Yeni ürün ekle"""
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            urun_kodu_val = urun_kodu if urun_kodu else None
            cursor.execute("""
                INSERT INTO stok (urun_kodu, urun_adi, marka, birim, stok_miktari, 
                                birim_fiyat, aciklama)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (urun_kodu_val, urun_adi, marka, birim, stok_miktari, birim_fiyat, aciklama))
            conn.commit()
            self.db.close()
            return True
        except sqlite3.IntegrityError:
            return False
        except Exception as e:
            print(f"Stok ekleme hatası: {e}")
            return False
    
    def stok_guncelle(self, stok_id: int, urun_kodu: str, urun_adi: str, 
                     marka: str, birim: str, stok_miktari: float, 
                     birim_fiyat: float, aciklama: str) -> bool:
        """Ürün bilgilerini güncelle"""
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            urun_kodu_val = urun_kodu if urun_kodu else None
            cursor.execute("""
                UPDATE stok 
                SET urun_kodu = ?, urun_adi = ?, marka = ?, birim = ?, stok_miktari = ?,
                    birim_fiyat = ?, aciklama = ?, guncelleme_tarihi = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (urun_kodu_val, urun_adi, marka, birim, stok_miktari, birim_fiyat, aciklama, stok_id))
            conn.commit()
            self.db.close()
            return True
        except sqlite3.IntegrityError:
            return False
        except Exception as e:
            print(f"Stok güncelleme hatası: {e}")
            return False
    
    def stok_sil(self, stok_id: int) -> bool:
        """Ürünü sil"""
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM stok WHERE id = ?", (stok_id,))
            conn.commit()
            self.db.close()
            return True
        except Exception as e:
            print(f"Stok silme hatası: {e}")
            return False
    
    def stok_listele(self, arama: str = "") -> List[Dict]:
        """Tüm ürünleri listele"""
        conn = self.db.connect()
        cursor = conn.cursor()
        
        if arama:
            cursor.execute("""
                SELECT * FROM stok 
                WHERE urun_kodu LIKE ? OR urun_adi LIKE ? OR marka LIKE ?
                ORDER BY urun_adi
            """, (f"%{arama}%", f"%{arama}%", f"%{arama}%"))
        else:
            cursor.execute("SELECT * FROM stok ORDER BY urun_adi")
        
        rows = cursor.fetchall()
        self.db.close()
        return [dict(row) for row in rows]
    
    def stok_getir(self, stok_id: int) -> Optional[Dict]:
        """Belirli bir ürünü getir"""
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM stok WHERE id = ?", (stok_id,))
        row = cursor.fetchone()
        self.db.close()
        return dict(row) if row else None
    
    def stok_urun_adi_ile_ara(self, urun_adi: str) -> Optional[Dict]:
        """Ürün adı ile ürün ara"""
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM stok WHERE urun_adi = ?", (urun_adi,))
        row = cursor.fetchone()
        self.db.close()
        return dict(row) if row else None
    
    def stok_urun_kodu_ile_ara(self, urun_kodu: str) -> Optional[Dict]:
        """Ürün kodu ile ürün ara"""
        if not urun_kodu or not urun_kodu.strip():
            return None
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM stok WHERE urun_kodu = ?", (urun_kodu.strip(),))
        row = cursor.fetchone()
        self.db.close()
        return dict(row) if row else None
    
    def stok_miktar_azalt(self, urun_kodu: str, miktar: float) -> Tuple[bool, str]:
        """Ürün koduna göre stok miktarını azalt"""
        if not urun_kodu or not urun_kodu.strip():
            return (False, "Ürün kodu boş olamaz")
        
        conn = None
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            cursor.execute("SELECT id, stok_miktari, urun_adi FROM stok WHERE urun_kodu = ?", (urun_kodu.strip(),))
            row = cursor.fetchone()
            
            if not row:
                self.db.close()
                return (False, f"Ürün kodu '{urun_kodu}' stokta bulunamadı")
            
            stok_id, mevcut_miktar, urun_adi = row['id'], row['stok_miktari'], row['urun_adi']
            
            if mevcut_miktar < miktar:
                self.db.close()
                return (False, f"Yetersiz stok! Mevcut: {mevcut_miktar}, İstenen: {miktar} (Ürün: {urun_adi})")
            
            yeni_miktar = mevcut_miktar - miktar
            cursor.execute("""
                UPDATE stok 
                SET stok_miktari = ?, guncelleme_tarihi = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (yeni_miktar, stok_id))
            
            conn.commit()
            self.db.close()
            return (True, f"Stok güncellendi: {urun_adi} (Kalan: {yeni_miktar})")
            
        except Exception as e:
            if conn:
                conn.rollback()
                self.db.close()
            return (False, f"Stok azaltma hatası: {str(e)}")
    
    def stok_miktar_azalt_batch(self, urunler: List[Dict[str, Any]]) -> Tuple[List[str], List[str]]:
        """Birden fazla ürünün stok miktarını tek bir transaction içinde azalt"""
        basarili_mesajlar = []
        hata_mesajlari = []
        
        if not urunler:
            return (basarili_mesajlar, hata_mesajlari)
        
        conn = None
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            
            urun_bilgileri = []
            for urun in urunler:
                urun_kodu = urun.get("urun_kodu", "").strip()
                miktar = urun.get("miktar", 0)
                urun_adi = urun.get("urun_adi", "")
                
                if not urun_kodu:
                    hata_mesajlari.append(f"{urun_adi or 'Bilinmeyen'}: Ürün kodu boş")
                    continue
                
                if miktar <= 0:
                    hata_mesajlari.append(f"{urun_adi} ({urun_kodu}): Miktar 0'dan büyük olmalıdır")
                    continue
                
                cursor.execute("SELECT id, stok_miktari, urun_adi FROM stok WHERE urun_kodu = ?", (urun_kodu,))
                row = cursor.fetchone()
                
                if not row:
                    hata_mesajlari.append(f"{urun_adi} ({urun_kodu}): Stokta bulunamadı")
                    continue
                
                stok_id, mevcut_miktar, db_urun_adi = row['id'], row['stok_miktari'], row['urun_adi']
                
                if mevcut_miktar < miktar:
                    hata_mesajlari.append(f"{db_urun_adi} ({urun_kodu}): Yetersiz stok! Mevcut: {mevcut_miktar}, İstenen: {miktar}")
                    continue
                
                urun_bilgileri.append({
                    "stok_id": stok_id,
                    "urun_kodu": urun_kodu,
                    "urun_adi": db_urun_adi,
                    "mevcut_miktar": mevcut_miktar,
                    "miktar": miktar
                })
            
            if hata_mesajlari and not urun_bilgileri:
                conn.rollback()
                return (basarili_mesajlar, hata_mesajlari)
            
            for urun_info in urun_bilgileri:
                yeni_miktar = urun_info["mevcut_miktar"] - urun_info["miktar"]
                cursor.execute("""
                    UPDATE stok 
                    SET stok_miktari = ?, guncelleme_tarihi = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (yeni_miktar, urun_info["stok_id"]))
                basarili_mesajlar.append(f"{urun_info['urun_adi']} ({urun_info['urun_kodu']}): Stok güncellendi (Kalan: {yeni_miktar})")
            
            conn.commit()
            return (basarili_mesajlar, hata_mesajlari)
            
        except Exception as e:
            if conn:
                try:
                    conn.rollback()
                except:
                    pass
            hata_mesajlari.append(f"Toplu stok azaltma hatası: {str(e)}")
            return (basarili_mesajlar, hata_mesajlari)
        finally:
            self.db.close()

