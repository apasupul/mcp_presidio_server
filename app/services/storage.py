import sqlite3
from pathlib import Path
from typing import Dict, List

DB_PATH = Path(__file__).resolve().parents[1] / "data.db"

def _init():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS mappings(
            session_id TEXT NOT NULL,
            placeholder TEXT NOT NULL,
            original TEXT NOT NULL,
            PRIMARY KEY (session_id, placeholder)
        )""")
        c.execute("""
        CREATE TABLE IF NOT EXISTS sessions(
            session_id TEXT PRIMARY KEY,
            created_at TEXT
        )""")
        conn.commit()

_init()

def create_session(session_id: str):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("INSERT OR IGNORE INTO sessions(session_id, created_at) VALUES (?, datetime('now'))",
                     (session_id,))
        conn.commit()

def save_mappings(session_id: str, mapping: Dict[str, str]):
    with sqlite3.connect(DB_PATH) as conn:
        conn.executemany("INSERT OR REPLACE INTO mappings(session_id, placeholder, original) VALUES (?,?,?)",
                         [(session_id, ph, orig) for ph, orig in mapping.items()])
        conn.commit()

def get_mapping(session_id: str) -> Dict[str, str]:
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute("SELECT placeholder, original FROM mappings WHERE session_id=?", (session_id,)).fetchall()
    return {ph: orig for ph, orig in rows}

def list_sessions() -> List[str]:
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute("SELECT session_id FROM sessions ORDER BY created_at DESC").fetchall()
    return [r[0] for r in rows]
