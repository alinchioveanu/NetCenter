import sqlite3
from pathlib import Path

DB_PATH = Path("/app/data/netcenter.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
    CREATE TABLE IF NOT EXISTS boot_images(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        boot_type TEXT NOT NULL,
        path TEXT NOT NULL,
        enabled INTEGER DEFAULT 1,
        sort_order INTEGER DEFAULT 0,
        description TEXT DEFAULT '',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()
