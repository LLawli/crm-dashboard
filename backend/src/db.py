import sqlite3
from src.config import DB_PATH

def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)