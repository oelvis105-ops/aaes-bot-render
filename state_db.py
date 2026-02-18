import sqlite3, json, os
from pathlib import Path

DB_FILE = Path(__file__).with_name("bot_state.db")

def _get_conn():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS user_state (
            user_id INTEGER PRIMARY KEY,
            state   TEXT,
            data    TEXT
        )
    """)
    conn.commit()
    return conn

def get_state(user_id: int) -> dict:
    with _get_conn() as conn:
        row = conn.execute("SELECT state, data FROM user_state WHERE user_id=?", (user_id,)).fetchone()
        if not row:
            return {}
        return {"state": row[0], "data": json.loads(row[1] or "{}")}

def set_state(user_id: int, state: str, data: dict | None = None):
    with _get_conn() as conn:
        conn.execute(
            "REPLACE INTO user_state(user_id, state, data) VALUES (?,?,?)",
            (user_id, state, json.dumps(data or {}))
        )
        conn.commit()