import os
import json
from collections import defaultdict

try:
    import psycopg2
    _DATABASE_URL = os.getenv("DATABASE_URL")
    _db_enabled = bool(_DATABASE_URL)
except ImportError:
    _db_enabled = False
    _DATABASE_URL = None

_memory_store: dict = defaultdict(list)


def _get_conn():
    return psycopg2.connect(_DATABASE_URL)


def _init_db() -> bool:
    try:
        conn = _get_conn()
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS chat_sessions (
                        session_id TEXT        PRIMARY KEY,
                        messages   JSONB       NOT NULL DEFAULT '[]',
                        created_at TIMESTAMPTZ DEFAULT NOW(),
                        updated_at TIMESTAMPTZ DEFAULT NOW()
                    )
                """)
        conn.close()
        return True
    except Exception as e:
        print(f"DB init failed, using in-memory store: {e}")
        return False


if _db_enabled:
    _db_enabled = _init_db()


def get_history(session_id: str) -> list:
    if _db_enabled:
        try:
            conn = _get_conn()
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT messages FROM chat_sessions WHERE session_id = %s",
                    (session_id,),
                )
                row = cur.fetchone()
            conn.close()
            return row[0] if row else []
        except Exception as e:
            print(f"DB read error: {e}")
    return list(_memory_store[session_id])


def save_history(session_id: str, messages: list) -> None:
    if _db_enabled:
        try:
            conn = _get_conn()
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO chat_sessions (session_id, messages, updated_at)
                        VALUES (%s, %s::jsonb, NOW())
                        ON CONFLICT (session_id) DO UPDATE
                        SET messages = EXCLUDED.messages, updated_at = NOW()
                        """,
                        (session_id, json.dumps(messages)),
                    )
            conn.close()
            return
        except Exception as e:
            print(f"DB write error: {e}")
    _memory_store[session_id] = messages
