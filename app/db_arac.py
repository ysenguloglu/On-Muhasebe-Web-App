"""
Araç Yönetimi (Modül 2) veritabanı işlemleri
Araç kartı, belge takibi, bakım geçmişi
"""
from typing import Optional, List, Dict, Tuple, Any
from .db_connection import DatabaseConnection


# Sabitler
ARAC_TIPLERI = ("çekici", "dorse", "diğer")
ARAC_DURUMLARI = ("aktif", "bakımda", "pasif")
BELGE_TURLERI = (
    "araç muayenesi",
    "trafik sigortası",
    "kasko",
    "egzoz muayenesi",
    "ADR sertifikası",
    "araç ruhsatı",
)
BAKIM_TURLERI = ("yağ değişimi", "fren kontrolü", "lastik değişimi", "genel bakım")

# Bakım uyarı kuralları: (bakim_turu, km_aralik, ay_aralik, yil_aralik)
# yil_aralik/ay_aralik None ise sadece km kullanılır
BAKIM_UYARI_KURALLARI = [
    ("yağ değişimi", 15000, 6, None),
    ("fren kontrolü", 25000, None, None),
    ("lastik değişimi", 80000, None, 3),
]


class AracDB:
    """Araç yönetimi veritabanı işlemleri"""

    def __init__(self, db_conn: DatabaseConnection):
        self.db = db_conn

    def arac_ekle(
        self,
        arac_plakasi: str,
        arac_tipi: str = "diğer",
        marka: str = "",
        model: str = "",
        model_yili: Optional[int] = None,
        sasi_no: str = "",
        motor_no: str = "",
        guncel_km: float = 0,
        alis_tarihi: Optional[str] = None,
        alis_fiyati: Optional[float] = None,
        durum: str = "aktif",
    ) -> Tuple[bool, str]:
        """Yeni araç ekler. Plaka benzersiz ve zorunlu."""
        arac_plakasi = (arac_plakasi or "").strip().upper()
        if not arac_plakasi:
            return (False, "Araç plakası zorunludur.")
        if arac_tipi not in ARAC_TIPLERI:
            arac_tipi = "diğer"
        if durum not in ARAC_DURUMLARI:
            durum = "aktif"
        if sasi_no and len(sasi_no.strip()) != 17:
            return (False, "Şasi numarası (VIN) 17 karakter olmalıdır.")
        conn = None
        try:
            conn = self.db.connect()
            cursor = self.db._get_cursor(conn)
            q = """
                INSERT INTO arac (arac_plakasi, arac_tipi, marka, model, model_yili,
                    sasi_no, motor_no, guncel_km, alis_tarihi, alis_fiyati, durum)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            q = self.db._convert_placeholders(q)
            cursor.execute(
                q,
                (
                    arac_plakasi,
                    arac_tipi,
                    marka or None,
                    model or None,
                    model_yili,
                    sasi_no.strip() or None,
                    motor_no.strip() or None,
                    float(guncel_km),
                    alis_tarihi,
                    float(alis_fiyati) if alis_fiyati is not None else None,
                    durum,
                ),
            )
            conn.commit()
            return (True, "Araç eklendi.")
        except Exception as e:
            if conn:
                try:
                    conn.rollback()
                except Exception:
                    pass
            if self.db._is_integrity_error(e):
                return (False, "Bu plaka zaten kayıtlı.")
            return (False, str(e))
        finally:
            self.db.close()

    def arac_guncelle(
        self,
        arac_id: int,
        arac_plakasi: str,
        arac_tipi: str,
        marka: str,
        model: str,
        model_yili: Optional[int],
        sasi_no: str,
        motor_no: str,
        guncel_km: float,
        alis_tarihi: Optional[str],
        alis_fiyati: Optional[float],
        durum: str,
    ) -> Tuple[bool, str]:
        """Araç bilgilerini günceller."""
        arac_plakasi = (arac_plakasi or "").strip().upper()
        if not arac_plakasi:
            return (False, "Araç plakası zorunludur.")
        if arac_tipi not in ARAC_TIPLERI:
            arac_tipi = "diğer"
        if durum not in ARAC_DURUMLARI:
            durum = "aktif"
        if sasi_no and len(sasi_no.strip()) != 17:
            return (False, "Şasi numarası (VIN) 17 karakter olmalıdır.")
        conn = None
        try:
            conn = self.db.connect()
            cursor = self.db._get_cursor(conn)
            q = """
                UPDATE arac SET arac_plakasi=?, arac_tipi=?, marka=?, model=?,
                    model_yili=?, sasi_no=?, motor_no=?, guncel_km=?, alis_tarihi=?,
                    alis_fiyati=?, durum=?, guncelleme_tarihi=CURRENT_TIMESTAMP
                WHERE id=?
            """
            q = self.db._convert_placeholders(q)
            cursor.execute(
                q,
                (
                    arac_plakasi,
                    arac_tipi,
                    marka or None,
                    model or None,
                    model_yili,
                    sasi_no.strip() or None,
                    motor_no.strip() or None,
                    float(guncel_km),
                    alis_tarihi,
                    float(alis_fiyati) if alis_fiyati is not None else None,
                    durum,
                    arac_id,
                ),
            )
            conn.commit()
            return (True, "Araç güncellendi.")
        except Exception as e:
            if conn:
                try:
                    conn.rollback()
                except Exception:
                    pass
            if self.db._is_integrity_error(e):
                return (False, "Bu plaka başka bir araçta kayıtlı.")
            return (False, str(e))
        finally:
            self.db.close()

    def arac_sil(self, arac_id: int) -> bool:
        """Aracı siler (cascade ile belge ve bakım kayıtları da silinir)."""
        conn = None
        try:
            conn = self.db.connect()
            cursor = self.db._get_cursor(conn)
            q = "DELETE FROM arac WHERE id = ?"
            q = self.db._convert_placeholders(q)
            cursor.execute(q, (arac_id,))
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
            return False

    def arac_listele(self, arama: str = "", durum: Optional[str] = None) -> List[Dict]:
        """Tüm araçları listeler."""
        conn = self.db.connect()
        cursor = self.db._get_cursor(conn)
        if arama or durum:
            conditions = []
            params = []
            if arama:
                conditions.append("(arac_plakasi LIKE ? OR marka LIKE ? OR model LIKE ? OR sasi_no LIKE ?)")
                p = f"%{arama}%"
                params.extend([p, p, p, p])
            if durum:
                conditions.append("durum = ?")
                params.append(durum)
            where = " AND ".join(conditions)
            q = f"SELECT * FROM arac WHERE {where} ORDER BY arac_plakasi"
            q = self.db._convert_placeholders(q)
            cursor.execute(q, tuple(params))
        else:
            q = "SELECT * FROM arac ORDER BY arac_plakasi"
            cursor.execute(q)
        rows = cursor.fetchall()
        self.db.close()
        return [dict(r) for r in rows] if rows else []

    def arac_getir(self, arac_id: int) -> Optional[Dict]:
        """Tek araç getirir."""
        conn = self.db.connect()
        cursor = self.db._get_cursor(conn)
        q = "SELECT * FROM arac WHERE id = ?"
        q = self.db._convert_placeholders(q)
        cursor.execute(q, (arac_id,))
        row = cursor.fetchone()
        self.db.close()
        return dict(row) if row else None

    def arac_plaka_ile_getir(self, plaka: str) -> Optional[Dict]:
        """Plakaya göre araç getirir."""
        conn = self.db.connect()
        cursor = self.db._get_cursor(conn)
        q = "SELECT * FROM arac WHERE arac_plakasi = ?"
        q = self.db._convert_placeholders(q)
        cursor.execute(q, (plaka.strip().upper(),))
        row = cursor.fetchone()
        self.db.close()
        return dict(row) if row else None

    # ---------- Belge ----------
    def belge_ekle(
        self,
        arac_id: int,
        belge_turu: str,
        duzenlenme_tarihi: Optional[str],
        bitis_tarihi: str,
        belge_dosya_path: Optional[str] = None,
    ) -> Tuple[bool, str]:
        """Araca belge ekler."""
        conn = None
        try:
            conn = self.db.connect()
            cursor = self.db._get_cursor(conn)
            q = """
                INSERT INTO arac_belge (arac_id, belge_turu, duzenlenme_tarihi, bitis_tarihi, belge_dosya_path)
                VALUES (?, ?, ?, ?, ?)
            """
            q = self.db._convert_placeholders(q)
            cursor.execute(q, (arac_id, belge_turu, duzenlenme_tarihi, bitis_tarihi, belge_dosya_path))
            conn.commit()
            return (True, "Belge eklendi.")
        except Exception as e:
            if conn:
                try:
                    conn.rollback()
                except Exception:
                    pass
            return (False, str(e))
        finally:
            self.db.close()

    def belge_listele(self, arac_id: int) -> List[Dict]:
        """Aracın belgelerini listeler."""
        conn = self.db.connect()
        cursor = self.db._get_cursor(conn)
        q = "SELECT * FROM arac_belge WHERE arac_id = ? ORDER BY bitis_tarihi ASC"
        q = self.db._convert_placeholders(q)
        cursor.execute(q, (arac_id,))
        rows = cursor.fetchall()
        self.db.close()
        return [dict(r) for r in rows] if rows else []

    def belge_suresi_dolacak_listele(self, gun: int = 30) -> List[Dict]:
        """Belirtilen gün sayısı içinde süresi dolacak belgeleri listeler (tüm araçlar)."""
        conn = self.db.connect()
        cursor = self.db._get_cursor(conn)
        q = """
            SELECT b.*, a.arac_plakasi, a.marka, a.model
            FROM arac_belge b
            JOIN arac a ON a.id = b.arac_id
            WHERE b.bitis_tarihi BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL ? DAY)
            ORDER BY b.bitis_tarihi ASC
        """
        q = self.db._convert_placeholders(q)
        cursor.execute(q, (gun,))
        rows = cursor.fetchall()
        self.db.close()
        return [dict(r) for r in rows] if rows else []

    def belge_takip_listele(
        self,
        arac_plakasi: Optional[str] = None,
        belge_turu: Optional[str] = None,
    ) -> List[Dict]:
        """Tüm araç belgelerini bitiş tarihine göre listeler (en yakın önce). Takip sekmesi için."""
        conn = self.db.connect()
        cursor = self.db._get_cursor(conn)
        conditions = []
        params = []
        if arac_plakasi and arac_plakasi.strip():
            conditions.append("a.arac_plakasi LIKE ?")
            params.append("%" + arac_plakasi.strip() + "%")
        if belge_turu and belge_turu.strip():
            conditions.append("b.belge_turu = ?")
            params.append(belge_turu.strip())
        where = " AND ".join(conditions) if conditions else "1=1"
        q = """
            SELECT b.id, b.arac_id, b.belge_turu, b.duzenlenme_tarihi, b.bitis_tarihi,
                   a.arac_plakasi
            FROM arac_belge b
            JOIN arac a ON a.id = b.arac_id
            WHERE """ + where + """
            ORDER BY b.bitis_tarihi ASC
        """
        q = self.db._convert_placeholders(q)
        cursor.execute(q, tuple(params))
        rows = cursor.fetchall()
        self.db.close()
        return [dict(r) for r in rows] if rows else []

    # ---------- Bakım ----------
    def bakim_ekle(
        self,
        arac_id: int,
        bakim_turu: str,
        aciklama: str = "",
        bakim_tarihi: str = "",
        bakim_km: Optional[float] = None,
        maliyet: Optional[float] = None,
    ) -> Tuple[bool, str]:
        """Araca bakım kaydı ekler. Bakım sonrası aracın güncel km güncellenebilir (opsiyonel)."""
        conn = None
        try:
            conn = self.db.connect()
            cursor = self.db._get_cursor(conn)
            q = """
                INSERT INTO arac_bakim (arac_id, bakim_turu, aciklama, bakim_tarihi, bakim_km, maliyet)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            q = self.db._convert_placeholders(q)
            cursor.execute(q, (arac_id, bakim_turu, aciklama or None, bakim_tarihi, bakim_km, maliyet))
            conn.commit()
            return (True, "Bakım kaydı eklendi.")
        except Exception as e:
            if conn:
                try:
                    conn.rollback()
                except Exception:
                    pass
            return (False, str(e))
        finally:
            self.db.close()

    def bakim_listele(self, arac_id: int) -> List[Dict]:
        """Aracın bakım geçmişini listeler."""
        conn = self.db.connect()
        cursor = self.db._get_cursor(conn)
        q = "SELECT * FROM arac_bakim WHERE arac_id = ? ORDER BY bakim_tarihi DESC, id DESC"
        q = self.db._convert_placeholders(q)
        cursor.execute(q, (arac_id,))
        rows = cursor.fetchall()
        self.db.close()
        return [dict(r) for r in rows] if rows else []

    def bakim_uyarilari_hesapla(self, arac_id: int) -> List[Dict]:
        """
        Aracın bakım uyarılarını hesaplar.
        Yağ: 15.000 km veya 6 ay; Fren: 25.000 km; Lastik: 80.000 km veya 3 yıl.
        Dönen her öğe: bakim_turu, son_km, son_tarih, hedef_km, hedef_tarih, uyari_km, uyari_tarih
        """
        from datetime import datetime, date
        from calendar import monthrange

        def _tarihe_ay_ekle(d: date, ay: int) -> date:
            y, m = d.year, d.month
            m += ay
            while m > 12:
                m -= 12
                y += 1
            while m < 1:
                m += 12
                y -= 1
            gun = min(d.day, monthrange(y, m)[1])
            return date(y, m, gun)

        arac = self.arac_getir(arac_id)
        if not arac:
            return []
        guncel_km = float(arac.get("guncel_km") or 0)
        model_yili = arac.get("model_yili")
        uyarilar = []
        bakim_gecmisi = self.bakim_listele(arac_id)
        son_bakim: Dict[str, Dict] = {}
        for b in bakim_gecmisi:
            tur = b.get("bakim_turu")
            if tur not in son_bakim or (b.get("bakim_tarihi") or "") > (son_bakim[tur].get("bakim_tarihi") or ""):
                son_bakim[tur] = b

        bugun = date.today()
        for kural in BAKIM_UYARI_KURALLARI:
            bakim_turu, km_aralik, ay_aralik, yil_aralik = kural
            son = son_bakim.get(bakim_turu)
            son_km = float(son.get("bakim_km") or 0) if son else 0
            son_tarih = son.get("bakim_tarihi") if son else None
            hedef_km = son_km + km_aralik
            uyari_km = guncel_km >= hedef_km if km_aralik else False
            uyari_tarih = False
            hedef_tarih = None
            if ay_aralik and son_tarih:
                try:
                    dt = datetime.strptime(son_tarih[:10], "%Y-%m-%d").date()
                    hedef_dt = _tarihe_ay_ekle(dt, ay_aralik)
                    hedef_tarih = hedef_dt.strftime("%Y-%m-%d")
                    uyari_tarih = bugun >= hedef_dt
                except Exception:
                    pass
            if yil_aralik is not None and (model_yili or son_tarih):
                try:
                    yil = int(son_tarih[:4]) if son_tarih else (model_yili or bugun.year)
                    hedef_yil = yil + yil_aralik
                    uyari_tarih = bugun.year >= hedef_yil
                    hedef_tarih = f"{hedef_yil}-12-31"
                except Exception:
                    pass
            if uyari_km or uyari_tarih:
                uyarilar.append({
                    "bakim_turu": bakim_turu,
                    "son_km": son_km,
                    "son_tarih": son_tarih,
                    "hedef_km": hedef_km,
                    "hedef_tarih": hedef_tarih,
                    "guncel_km": guncel_km,
                    "uyari_km": uyari_km,
                    "uyari_tarih": uyari_tarih,
                })
        return uyarilar
