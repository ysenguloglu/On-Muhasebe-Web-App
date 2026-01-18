"""
İş evrakı veritabanı işlemleri
"""
from typing import List, Dict
from .db_connection import DatabaseConnection


class IsEvrakiDB:
    """İş evrakı veritabanı işlemleri"""
    
    def __init__(self, db_conn: DatabaseConnection):
        self.db = db_conn
    
    def is_evraki_ekle(self, is_emri_no: int, tarih: str, musteri_unvan: str,
                      telefon: str = "", arac_plakasi: str = "", cekici_dorse: str = "",
                      marka_model: str = "", talep_edilen_isler: str = "",
                      musteri_sikayeti: str = "", yapilan_is: str = "",
                      baslama_saati: str = "", bitis_saati: str = "",
                      kullanilan_urunler: str = "", toplam_tutar: float = 0,
                      tc_kimlik_no: str = "") -> tuple[bool, str]:
        """Yeni iş evrakı ekle"""
        conn = None
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            
            telefon_val = telefon if telefon else None
            arac_plakasi_val = arac_plakasi if arac_plakasi else None
            cekici_dorse_val = cekici_dorse if cekici_dorse else None
            marka_model_val = marka_model if marka_model else None
            talep_edilen_isler_val = talep_edilen_isler if talep_edilen_isler else None
            musteri_sikayeti_val = musteri_sikayeti if musteri_sikayeti else None
            yapilan_is_val = yapilan_is if yapilan_is else None
            baslama_saati_val = baslama_saati if baslama_saati else None
            bitis_saati_val = bitis_saati if bitis_saati else None
            kullanilan_urunler_val = kullanilan_urunler if kullanilan_urunler else None
            tc_kimlik_no_val = tc_kimlik_no.strip() if tc_kimlik_no and tc_kimlik_no.strip() else None
            
            query = """
                INSERT INTO is_evraki (is_emri_no, tarih, musteri_unvan, telefon, arac_plakasi,
                                     cekici_dorse, marka_model, talep_edilen_isler, musteri_sikayeti,
                                     yapilan_is, baslama_saati, bitis_saati, kullanilan_urunler,
                                     toplam_tutar, tc_kimlik_no)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            query = self.db._convert_placeholders(query)
            cursor.execute(query, (is_emri_no, tarih, musteri_unvan, telefon_val, arac_plakasi_val, cekici_dorse_val,
                  marka_model_val, talep_edilen_isler_val, musteri_sikayeti_val, yapilan_is_val,
                  baslama_saati_val, bitis_saati_val, kullanilan_urunler_val, toplam_tutar, tc_kimlik_no_val))
            conn.commit()
            return (True, "İş evrakı başarıyla kaydedildi")
        except Exception as e:
            hata_mesaji = f"Veritabanı hatası: {str(e)}"
            print(f"İş evrakı ekleme hatası: {e}")
            if conn:
                try:
                    conn.rollback()
                except:
                    pass
            return (False, hata_mesaji)
        except Exception as e:
            hata_mesaji = f"Beklenmeyen hata: {str(e)}"
            print(f"İş evrakı ekleme hatası: {e}")
            if conn:
                try:
                    conn.rollback()
                except:
                    pass
            return (False, hata_mesaji)
        finally:
            self.db.close()
    
    def is_evraki_listele(self) -> List[Dict]:
        """Tüm iş evraklarını listele"""
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM is_evraki ORDER BY olusturma_tarihi DESC")
        rows = cursor.fetchall()
        self.db.close()
        return [dict(row) for row in rows]
    
    def is_evraki_getir(self, evrak_id: int) -> Dict:
        """ID ile iş evrakı getir"""
        conn = self.db.connect()
        cursor = conn.cursor()
        query = "SELECT * FROM is_evraki WHERE id = ?"
        query = self.db._convert_placeholders(query)
        cursor.execute(query, (evrak_id,))
        row = cursor.fetchone()
        self.db.close()
        return dict(row) if row else None
    
    def is_evraki_guncelle(self, evrak_id: int, is_emri_no: int, tarih: str, musteri_unvan: str,
                           telefon: str = "", arac_plakasi: str = "", cekici_dorse: str = "",
                           marka_model: str = "", talep_edilen_isler: str = "",
                           musteri_sikayeti: str = "", yapilan_is: str = "",
                           baslama_saati: str = "", bitis_saati: str = "",
                           kullanilan_urunler: str = "", toplam_tutar: float = 0,
                           tc_kimlik_no: str = "") -> tuple[bool, str]:
        """İş evrakı güncelle"""
        conn = None
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            
            telefon_val = telefon if telefon else None
            arac_plakasi_val = arac_plakasi if arac_plakasi else None
            cekici_dorse_val = cekici_dorse if cekici_dorse else None
            marka_model_val = marka_model if marka_model else None
            talep_edilen_isler_val = talep_edilen_isler if talep_edilen_isler else None
            musteri_sikayeti_val = musteri_sikayeti if musteri_sikayeti else None
            yapilan_is_val = yapilan_is if yapilan_is else None
            baslama_saati_val = baslama_saati if baslama_saati else None
            bitis_saati_val = bitis_saati if bitis_saati else None
            kullanilan_urunler_val = kullanilan_urunler if kullanilan_urunler else None
            tc_kimlik_no_val = tc_kimlik_no.strip() if tc_kimlik_no and tc_kimlik_no.strip() else None
            
            query = """
                UPDATE is_evraki 
                SET is_emri_no = ?, tarih = ?, musteri_unvan = ?, telefon = ?, arac_plakasi = ?,
                    cekici_dorse = ?, marka_model = ?, talep_edilen_isler = ?, musteri_sikayeti = ?,
                    yapilan_is = ?, baslama_saati = ?, bitis_saati = ?, kullanilan_urunler = ?,
                    toplam_tutar = ?, tc_kimlik_no = ?
                WHERE id = ?
            """
            query = self.db._convert_placeholders(query)
            cursor.execute(query, (is_emri_no, tarih, musteri_unvan, telefon_val, arac_plakasi_val, cekici_dorse_val,
                  marka_model_val, talep_edilen_isler_val, musteri_sikayeti_val, yapilan_is_val,
                  baslama_saati_val, bitis_saati_val, kullanilan_urunler_val, toplam_tutar, tc_kimlik_no_val, evrak_id))
            conn.commit()
            
            if cursor.rowcount == 0:
                return (False, "İş evrakı bulunamadı")
            
            return (True, "İş evrakı başarıyla güncellendi")
        except Exception as e:
            hata_mesaji = f"Güncelleme hatası: {str(e)}"
            print(f"İş evrakı güncelleme hatası: {e}")
            if conn:
                try:
                    conn.rollback()
                except:
                    pass
            return (False, hata_mesaji)
        finally:
            self.db.close()
    
    def is_evraki_sil(self, evrak_id: int) -> tuple[bool, str]:
        """İş evrakı sil"""
        conn = None
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            query = "DELETE FROM is_evraki WHERE id = ?"
            query = self.db._convert_placeholders(query)
            cursor.execute(query, (evrak_id,))
            conn.commit()
            
            if cursor.rowcount == 0:
                return (False, "İş evrakı bulunamadı")
            
            return (True, "İş evrakı başarıyla silindi")
        except Exception as e:
            hata_mesaji = f"Silme hatası: {str(e)}"
            print(f"İş evrakı silme hatası: {e}")
            if conn:
                try:
                    conn.rollback()
                except:
                    pass
            return (False, hata_mesaji)
        finally:
            self.db.close()
    
    def is_emri_no_sonraki(self) -> int:
        """En küçük kullanılmayan pozitif iş emri numarasını döndür"""
        conn = self.db.connect()
        cursor = conn.cursor()
        
        # Tüm iş emri numaralarını al (pozitif olanlar)
        cursor.execute("SELECT DISTINCT is_emri_no FROM is_evraki WHERE is_emri_no > 0 ORDER BY is_emri_no")
        rows = cursor.fetchall()
        self.db.close()
        
        # Kullanılan numaraları set'e çevir
        kullanilan_nolar = {row[0] for row in rows}
        
        # 1'den başlayarak ilk kullanılmayan numarayı bul
        for numara in range(1, 10000):  # Maksimum 9999'a kadar kontrol et
            if numara not in kullanilan_nolar:
                return numara
        
        # Eğer 1-9999 arası hepsi doluysa, en büyük numaradan sonraki numarayı döndür
        if kullanilan_nolar:
            return max(kullanilan_nolar) + 1
        
        # Hiç kayıt yoksa 1 döndür
        return 1

