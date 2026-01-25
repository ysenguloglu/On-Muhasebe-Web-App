"""
Paylaşılan veritabanı örneği - MySQL
DATABASE_URL ortam değişkeni zorunludur.
"""
import os
from app.database import Database
from dotenv import load_dotenv

load_dotenv()

database_url = os.getenv("DATABASE_URL")

if not database_url or not (
    database_url.startswith("mysql://") or database_url.startswith("mysql+pymysql://")
):
    raise ValueError(
        "DATABASE_URL (MySQL) ortam değişkeni gerekli. "
        "Örnek: mysql://kullanici:sifre@host:3306/veritabani"
    )

db = Database(database_url=database_url)
