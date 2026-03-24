"""
Şoför Yönetimi veritabanı işlemleri
SRC / ehliyet / psikoteknik bitiş tarihleri ileride uyarı mantığı için DATE olarak tutulur.
"""
from typing import Optional, List, Dict, Tuple
from .db_connection import DatabaseConnection

SOFOR_DURUMLARI = ("aktif", "pasif")


class SoforDB:
    """Şoför kayıtları"""

    def __init__(self, db_conn: DatabaseConnection):
        self.db = db_conn

    def sofor_ekle(
        self,
        ad_soyad: str,
        tc_kimlik_no: str,
        telefon: str,
        email: Optional[str],
        adres: Optional[str],
        ise_baslama_tarihi: str,
        src_belge_no: str,
        src_bitis_tarihi: str,
        ehliyet_sinifi: str,
        ehliyet_bitis_tarihi: str,
        psikoteknik_bitis: str,
        acil_iletisim: str,
        iban: Optional[str],
        durum: str = "aktif",
    ) -> Tuple[bool, str]:
        ad_soyad = (ad_soyad or "").strip()
        tc_kimlik_no = (tc_kimlik_no or "").strip()
        telefon = (telefon or "").strip()
        if not ad_soyad or not tc_kimlik_no or not telefon:
            return (False, "Ad soyad, TC kimlik no ve telefon zorunludur.")
        if durum not in SOFOR_DURUMLARI:
            durum = "aktif"
        conn = None
        try:
            conn = self.db.connect()
            cursor = self.db._get_cursor(conn)
            q = """
                INSERT INTO sofor (
                    ad_soyad, tc_kimlik_no, telefon, email, adres,
                    ise_baslama_tarihi, src_belge_no, src_bitis_tarihi,
                    ehliyet_sinifi, ehliyet_bitis_tarihi, psikoteknik_bitis,
                    acil_iletisim, iban, durum
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            q = self.db._convert_placeholders(q)
            cursor.execute(
                q,
                (
                    ad_soyad,
                    tc_kimlik_no,
                    telefon,
                    email or None,
                    adres or None,
                    ise_baslama_tarihi,
                    src_belge_no.strip(),
                    src_bitis_tarihi,
                    ehliyet_sinifi.strip(),
                    ehliyet_bitis_tarihi,
                    psikoteknik_bitis,
                    acil_iletisim.strip(),
                    iban or None,
                    durum,
                ),
            )
            conn.commit()
            return (True, "Şoför eklendi.")
        except Exception as e:
            if conn:
                try:
                    conn.rollback()
                except Exception:
                    pass
            if self.db._is_integrity_error(e):
                return (False, "Bu TC kimlik numarası zaten kayıtlı.")
            return (False, str(e))
        finally:
            self.db.close()

    def sofor_guncelle(
        self,
        sofor_id: int,
        ad_soyad: str,
        tc_kimlik_no: str,
        telefon: str,
        email: Optional[str],
        adres: Optional[str],
        ise_baslama_tarihi: str,
        src_belge_no: str,
        src_bitis_tarihi: str,
        ehliyet_sinifi: str,
        ehliyet_bitis_tarihi: str,
        psikoteknik_bitis: str,
        acil_iletisim: str,
        iban: Optional[str],
        durum: str,
    ) -> Tuple[bool, str]:
        ad_soyad = (ad_soyad or "").strip()
        tc_kimlik_no = (tc_kimlik_no or "").strip()
        telefon = (telefon or "").strip()
        if not ad_soyad or not tc_kimlik_no or not telefon:
            return (False, "Ad soyad, TC kimlik no ve telefon zorunludur.")
        if durum not in SOFOR_DURUMLARI:
            durum = "aktif"
        conn = None
        try:
            conn = self.db.connect()
            cursor = self.db._get_cursor(conn)
            q = """
                UPDATE sofor SET
                    ad_soyad=?, tc_kimlik_no=?, telefon=?, email=?, adres=?,
                    ise_baslama_tarihi=?, src_belge_no=?, src_bitis_tarihi=?,
                    ehliyet_sinifi=?, ehliyet_bitis_tarihi=?, psikoteknik_bitis=?,
                    acil_iletisim=?, iban=?, durum=?,
                    guncelleme_tarihi=CURRENT_TIMESTAMP
                WHERE id=?
            """
            q = self.db._convert_placeholders(q)
            cursor.execute(
                q,
                (
                    ad_soyad,
                    tc_kimlik_no,
                    telefon,
                    email or None,
                    adres or None,
                    ise_baslama_tarihi,
                    src_belge_no.strip(),
                    src_bitis_tarihi,
                    ehliyet_sinifi.strip(),
                    ehliyet_bitis_tarihi,
                    psikoteknik_bitis,
                    acil_iletisim.strip(),
                    iban or None,
                    durum,
                    sofor_id,
                ),
            )
            conn.commit()
            return (True, "Şoför güncellendi.")
        except Exception as e:
            if conn:
                try:
                    conn.rollback()
                except Exception:
                    pass
            if self.db._is_integrity_error(e):
                return (False, "Bu TC kimlik numarası başka bir kayıtta kullanılıyor.")
            return (False, str(e))
        finally:
            self.db.close()

    def sofor_sil(self, sofor_id: int) -> bool:
        conn = None
        try:
            conn = self.db.connect()
            cursor = self.db._get_cursor(conn)
            q = "DELETE FROM sofor WHERE id = ?"
            q = self.db._convert_placeholders(q)
            cursor.execute(q, (sofor_id,))
            conn.commit()
            self.db.close()
            return True
        except Exception as e:
            if conn:
                try:
                    conn.rollback()
                except Exception:
                    pass
            self.db.close()
            print(f"Şoför silme hatası: {e}")
            return False

    def sofor_listele(self, arama: str = "", durum: Optional[str] = None) -> List[Dict]:
        conn = self.db.connect()
        cursor = self.db._get_cursor(conn)
        if arama or durum:
            conditions = []
            params = []
            if arama:
                conditions.append(
                    "(ad_soyad LIKE ? OR tc_kimlik_no LIKE ? OR telefon LIKE ? OR src_belge_no LIKE ?)"
                )
                p = f"%{arama}%"
                params.extend([p, p, p, p])
            if durum:
                conditions.append("durum = ?")
                params.append(durum)
            where = " AND ".join(conditions)
            q = f"SELECT * FROM sofor WHERE {where} ORDER BY ad_soyad"
            q = self.db._convert_placeholders(q)
            cursor.execute(q, tuple(params))
        else:
            cursor.execute("SELECT * FROM sofor ORDER BY ad_soyad")
        rows = cursor.fetchall()
        self.db.close()
        return [dict(r) for r in rows] if rows else []

    def sofor_getir(self, sofor_id: int) -> Optional[Dict]:
        conn = self.db.connect()
        cursor = self.db._get_cursor(conn)
        q = "SELECT * FROM sofor WHERE id = ?"
        q = self.db._convert_placeholders(q)
        cursor.execute(q, (sofor_id,))
        row = cursor.fetchone()
        self.db.close()
        return dict(row) if row else None
