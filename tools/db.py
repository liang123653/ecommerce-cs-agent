import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "database" / "ecommerce.db"

def fetch_one(table: str, order_id: str):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {table} WHERE order_id = ?", (order_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None
