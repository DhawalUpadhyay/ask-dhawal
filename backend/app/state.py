import os
import json
from collections import defaultdict
from datetime import datetime, timezone, timedelta

try:
    import psycopg2
    _DATABASE_URL = os.getenv("DATABASE_URL")
    _db_enabled = bool(_DATABASE_URL)
except ImportError:
    _db_enabled = False
    _DATABASE_URL = None

_memory_store: dict = defaultdict(list)
_meta_store: dict = {}  # session_id -> metadata dict


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
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS session_meta (
                        session_id      TEXT        PRIMARY KEY,
                        recruiter_name  TEXT,
                        recruiter_email TEXT        NOT NULL,
                        otp             TEXT        NOT NULL,
                        otp_expires_at  TIMESTAMPTZ NOT NULL,
                        verified        BOOLEAN     NOT NULL DEFAULT FALSE,
                        last_active_at  TIMESTAMPTZ DEFAULT NOW(),
                        summary_sent    BOOLEAN     NOT NULL DEFAULT FALSE,
                        created_at      TIMESTAMPTZ DEFAULT NOW()
                    )
                """)
        conn.close()
        return True
    except Exception as e:
        print(f"DB init failed, using in-memory store: {e}")
        return False


if _db_enabled:
    _db_enabled = _init_db()


# --- Session metadata ---

def create_session(session_id: str, name: str, email: str, otp: str, otp_expires_at: datetime) -> None:
    if _db_enabled:
        try:
            conn = _get_conn()
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO session_meta
                            (session_id, recruiter_name, recruiter_email, otp, otp_expires_at)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (session_id) DO NOTHING
                        """,
                        (session_id, name, email, otp, otp_expires_at),
                    )
            conn.close()
            return
        except Exception as e:
            print(f"DB create_session error: {e}")
    _meta_store[session_id] = {
        "recruiter_name": name,
        "recruiter_email": email,
        "otp": otp,
        "otp_expires_at": otp_expires_at,
        "verified": False,
        "last_active_at": datetime.now(timezone.utc),
        "summary_sent": False,
    }


def get_session_meta(session_id: str) -> dict | None:
    if _db_enabled:
        try:
            conn = _get_conn()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT recruiter_name, recruiter_email, otp, otp_expires_at,
                           verified, last_active_at, summary_sent
                    FROM session_meta WHERE session_id = %s
                    """,
                    (session_id,),
                )
                row = cur.fetchone()
            conn.close()
            if not row:
                return None
            return {
                "recruiter_name": row[0],
                "recruiter_email": row[1],
                "otp": row[2],
                "otp_expires_at": row[3],
                "verified": row[4],
                "last_active_at": row[5],
                "summary_sent": row[6],
            }
        except Exception as e:
            print(f"DB get_session_meta error: {e}")
    return _meta_store.get(session_id)


def verify_session(session_id: str) -> None:
    if _db_enabled:
        try:
            conn = _get_conn()
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "UPDATE session_meta SET verified = TRUE WHERE session_id = %s",
                        (session_id,),
                    )
            conn.close()
            return
        except Exception as e:
            print(f"DB verify_session error: {e}")
    if session_id in _meta_store:
        _meta_store[session_id]["verified"] = True


def update_last_active(session_id: str) -> None:
    now = datetime.now(timezone.utc)
    if _db_enabled:
        try:
            conn = _get_conn()
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "UPDATE session_meta SET last_active_at = %s WHERE session_id = %s",
                        (now, session_id),
                    )
            conn.close()
            return
        except Exception as e:
            print(f"DB update_last_active error: {e}")
    if session_id in _meta_store:
        _meta_store[session_id]["last_active_at"] = now


def mark_summary_sent(session_id: str) -> None:
    if _db_enabled:
        try:
            conn = _get_conn()
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "UPDATE session_meta SET summary_sent = TRUE WHERE session_id = %s",
                        (session_id,),
                    )
            conn.close()
            return
        except Exception as e:
            print(f"DB mark_summary_sent error: {e}")
    if session_id in _meta_store:
        _meta_store[session_id]["summary_sent"] = True


def get_idle_sessions(idle_minutes: int = 30) -> list:
    """Return verified, unsummarised sessions idle for longer than idle_minutes."""
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=idle_minutes)
    if _db_enabled:
        try:
            conn = _get_conn()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT sm.session_id, sm.recruiter_name, sm.recruiter_email,
                           cs.messages
                    FROM session_meta sm
                    LEFT JOIN chat_sessions cs ON cs.session_id = sm.session_id
                    WHERE sm.verified = TRUE
                      AND sm.summary_sent = FALSE
                      AND sm.last_active_at < %s
                    """,
                    (cutoff,),
                )
                rows = cur.fetchall()
            conn.close()
            return [
                {
                    "session_id": r[0],
                    "recruiter_name": r[1],
                    "recruiter_email": r[2],
                    "messages": r[3] or [],
                }
                for r in rows
            ]
        except Exception as e:
            print(f"DB get_idle_sessions error: {e}")
    result = []
    for sid, meta in _meta_store.items():
        last_active = meta.get("last_active_at", datetime.now(timezone.utc))
        if meta.get("verified") and not meta.get("summary_sent") and last_active < cutoff:
            result.append({
                "session_id": sid,
                "recruiter_name": meta.get("recruiter_name"),
                "recruiter_email": meta.get("recruiter_email"),
                "messages": list(_memory_store.get(sid, [])),
            })
    return result


# --- Chat history ---

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
