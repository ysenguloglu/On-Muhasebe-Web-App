"""
Kullanıcı ve rol yönetimi - veritabanı işlemleri
Roller: admin (her şeye yetkili), user (sadece iş evrakı yazma, diğerleri viewer)
"""
from typing import Optional, Tuple
from passlib.context import CryptContext

from .db_connection import DatabaseConnection

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


class AuthDB:
    def __init__(self, db_conn: DatabaseConnection):
        self.db = db_conn

    def get_user_by_username(self, username: str) -> Optional[dict]:
        """Kullanıcıyı kullanıcı adına göre getirir."""
        conn = None
        try:
            conn = self.db.connect()
            cursor = self.db._get_cursor(conn)
            q = "SELECT id, username, password_hash, role FROM users WHERE username = ?"
            q = self.db._convert_placeholders(q)
            cursor.execute(q, (username.strip(),))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            self.db.close()

    def authenticate(self, username: str, password: str) -> Optional[dict]:
        """Kullanıcı adı ve şifre ile doğrula. Başarılıysa kullanıcı dict (password_hash hariç)."""
        user = self.get_user_by_username(username)
        if not user or not verify_password(password, user["password_hash"]):
            return None
        out = {k: v for k, v in user.items() if k != "password_hash"}
        return out

    def seed_default_admin(self, default_password: str = "admin123") -> Tuple[bool, str]:
        """Hiç kullanıcı yoksa varsayılan admin ekler. Var olan verilere dokunmaz."""
        conn = None
        try:
            conn = self.db.connect()
            cursor = self.db._get_cursor(conn)
            cursor.execute("SELECT COUNT(*) as n FROM users")
            row = cursor.fetchone()
            n = (row.get("n") or 0) if row else 0
            if n > 0:
                return (False, "Zaten kullanıcı var, seed atlandı.")
            username = "admin"
            password_hash = hash_password(default_password)
            q = "INSERT INTO users (username, password_hash, role) VALUES (?, ?, 'admin')"
            q = self.db._convert_placeholders(q)
            cursor.execute(q, (username, password_hash))
            conn.commit()
            return (True, f"Varsayılan admin oluşturuldu (kullanıcı: {username}). İlk girişten sonra şifreyi değiştirin.")
        except Exception as e:
            if conn:
                try:
                    conn.rollback()
                except Exception:
                    pass
            return (False, str(e))
        finally:
            self.db.close()

    def list_users(self) -> list:
        """Tüm kullanıcıları listeler (password_hash hariç)."""
        conn = None
        try:
            conn = self.db.connect()
            cursor = self.db._get_cursor(conn)
            cursor.execute("SELECT id, username, role, olusturma_tarihi FROM users ORDER BY id")
            rows = cursor.fetchall()
            return [dict(r) for r in rows] if rows else []
        finally:
            self.db.close()

    def create_user(self, username: str, password: str, role: str = "user") -> Tuple[bool, str]:
        """Yeni kullanıcı ekler. role: admin veya user. Başarılıysa (True, mesaj), değilse (False, hata)."""
        username = (username or "").strip()
        if not username:
            return (False, "Kullanıcı adı boş olamaz.")
        if role not in ("admin", "user"):
            return (False, "Rol 'admin' veya 'user' olmalıdır.")
        if self.get_user_by_username(username):
            return (False, "Bu kullanıcı adı zaten kullanılıyor.")
        conn = None
        try:
            conn = self.db.connect()
            cursor = self.db._get_cursor(conn)
            password_hash = hash_password(password)
            q = "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)"
            q = self.db._convert_placeholders(q)
            cursor.execute(q, (username, password_hash, role))
            conn.commit()
            return (True, f"Kullanıcı '{username}' oluşturuldu.")
        except Exception as e:
            if conn:
                try:
                    conn.rollback()
                except Exception:
                    pass
            return (False, str(e))
        finally:
            self.db.close()

    def delete_user(self, user_id: int) -> Tuple[bool, str]:
        """Kullanıcıyı siler. Son kalan admin silinemez."""
        conn = None
        try:
            conn = self.db.connect()
            cursor = self.db._get_cursor(conn)
            q_usr = "SELECT id, role FROM users WHERE id = ?"
            cursor.execute(self.db._convert_placeholders(q_usr), (user_id,))
            row = cursor.fetchone()
            if not row:
                return (False, "Kullanıcı bulunamadı.")
            if row.get("role") == "admin":
                cursor.execute("SELECT COUNT(*) as n FROM users WHERE role = 'admin'")
                cnt = cursor.fetchone()
                n_admin = (cnt.get("n") or 0) if cnt else 0
                if n_admin <= 1:
                    return (False, "En az bir admin hesabı kalmalıdır. Silmek için önce başka bir admin ekleyin.")
            q_del = "DELETE FROM users WHERE id = ?"
            cursor.execute(self.db._convert_placeholders(q_del), (user_id,))
            conn.commit()
            return (True, "Kullanıcı silindi.")
        except Exception as e:
            if conn:
                try:
                    conn.rollback()
                except Exception:
                    pass
            return (False, str(e))
        finally:
            self.db.close()
