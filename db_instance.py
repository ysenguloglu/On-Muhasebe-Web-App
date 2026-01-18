"""
Shared database instance for all modules
This ensures all modules use the same database connection to avoid "database is locked" errors
"""
import os
from app.database import Database
from dotenv import load_dotenv

load_dotenv()

# DATABASE_URL varsa MySQL, yoksa SQLite kullan
database_url = os.getenv("DATABASE_URL")

# Single database instance shared across all modules
# MySQL URL formatı: mysql://user:password@host:port/database veya mysql+pymysql://...
if database_url and (database_url.startswith("mysql://") or database_url.startswith("mysql+pymysql://")):
    # MySQL kullan
    db = Database(database_url=database_url)
else:
    # SQLite kullan (varsayılan)
    db = Database()
