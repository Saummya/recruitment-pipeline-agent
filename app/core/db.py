import sqlite3

from app.core.config import DB_PATH


def get_connection() -> sqlite3.Connection:
    # mode=ro opens the file READ-ONLY. Even if a bad query slips through
    # our checks, the database itself refuses to change.
    return sqlite3.connect(f"{DB_PATH.as_uri()}?mode=ro", uri=True)


def get_schema() -> str:
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND sql IS NOT NULL"
        ).fetchall()
    finally:
        conn.close()
    return "\n\n".join(r[0] for r in rows)


def run_query(sql: str):
    conn = get_connection()
    try:
        cur = conn.execute(sql)
        columns = [d[0] for d in cur.description]
        return columns, cur.fetchall()
    finally:
        conn.close()