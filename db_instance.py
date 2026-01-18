"""
Shared database instance for all modules
This ensures all modules use the same database connection to avoid "database is locked" errors
"""
from app.database import Database

# Single database instance shared across all modules
db = Database()
