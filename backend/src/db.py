import sqlite3
from src.config import DB_PATH
import re
from pathlib import Path

match = re.match(r"^sqlite:///(.+)$", DB_PATH or "")
if not match:
    raise ValueError("DATABASE_URL invalid or not in config")

relative_path = match.group(1)
db_path = Path(relative_path).resolve()

def get_connection():
    return sqlite3.connect(db_path, check_same_thread=False)

def init_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
CREATE TABLE IF NOT EXISTS campaigns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
)
"""
    )
    conn.commit()
    conn.close()