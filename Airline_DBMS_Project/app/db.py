"""Database connection helper for the Airline application."""
import sqlite3, os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH  = os.path.join(BASE_DIR, "database", "airline.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables and load seed data if database is empty."""
    schema = os.path.join(BASE_DIR, "database", "schema.sql")
    seed   = os.path.join(BASE_DIR, "database", "seed.sql")
    conn = get_db()
    cur  = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
    if cur.fetchone()[0] < 3:
        with open(schema) as f:
            conn.executescript(f.read())
        with open(seed) as f:
            conn.executescript(f.read())
        conn.commit()
    conn.close()


def query(sql, params=(), one=False):
    conn = get_db()
    cur  = conn.execute(sql, params)
    rows = cur.fetchone() if one else cur.fetchall()
    conn.close()
    return rows


def mutate(sql, params=()):
    """Execute INSERT/UPDATE/DELETE, return lastrowid."""
    conn = get_db()
    try:
        cur = conn.execute(sql, params)
        conn.commit()
        rowid = cur.lastrowid
    except sqlite3.Error:
        conn.rollback()
        raise
    finally:
        conn.close()
    return rowid


def mutate_many(ops):
    """Execute multiple (sql, params) in one transaction."""
    conn = get_db()
    try:
        for sql, params in ops:
            conn.execute(sql, params)
        conn.commit()
    except sqlite3.Error:
        conn.rollback()
        raise
    finally:
        conn.close()
