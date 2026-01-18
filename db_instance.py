"""
Shared database instance for all modules
This ensures all modules use the same database connection to avoid "database is locked" errors
"""
import os
from app.database import Database
from dotenv import load_dotenv

load_dotenv()

# DATABASE_URL varsa PostgreSQL, yoksa SQLite kullan
database_url = os.getenv("DATABASE_URL")

# Single database instance shared across all modules
# Railway bazen postgres:// veya postgresql:// formatında URL verebilir
if database_url and (database_url.startswith("postgresql://") or database_url.startswith("postgres://")):
    # PostgreSQL kullan
    db = Database(database_url=database_url)
else:
    # SQLite kullan (varsayılan)
    db = Database()
