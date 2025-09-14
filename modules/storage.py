# modules/storage.py
from __future__ import annotations
from sqlalchemy import create_engine, text as sa_text
from sqlalchemy.pool import StaticPool
import json
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Any, Dict, Optional, List

# Single app DB (auth can remain in data/auth.db from auth.py)
_DB_PATH = "sqlite:///noctimind.db"

_engine = create_engine(
    _DB_PATH,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

# ---------- Schema & Migration ----------

def _column_exists(conn, table: str, column: str) -> bool:
    info = conn.execute(sa_text(f"PRAGMA table_info({table})")).fetchall()
    cols = {row[1] for row in info}  # (cid, name, type, notnull, dflt_value, pk)
    return column in cols

def init_db():
    """Create base table (if not present) and ensure user scoping column/index exist."""
    with _engine.begin() as conn:
        # Base table (no user column here; we add/migrate below)
        conn.execute(sa_text("""
        CREATE TABLE IF NOT EXISTS dreams (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          created_at TEXT NOT NULL,
          text TEXT NOT NULL,
          tags TEXT,
          sleep_hours REAL,
          sleep_quality INTEGER,
          motifs TEXT,
          archetype TEXT,
          reframed TEXT,
          emotions TEXT,
          embedding BLOB
        )
        """))

        # Add user_email column if missing
        if not _column_exists(conn, "dreams", "user_email"):
            # SQLite (>=3.35) supports IF NOT EXISTS; fallback: try without IF NOT EXISTS
            try:
                conn.execute(sa_text("ALTER TABLE dreams ADD COLUMN user_email TEXT"))
            except Exception:
                # In rare cases on very old SQLite, migration may require a copy table approach.
                # Most environments will succeed with the simple ALTER.
                pass

        # Create an index for faster per-user queries
        # SQLite supports IF NOT EXISTS for indexes.
        conn.execute(sa_text("CREATE INDEX IF NOT EXISTS idx_dreams_user_email ON dreams(user_email)"))

# Call on import so app has schema ready
init_db()

# ---------- Insert & Fetch (Per-User) ----------

def _to_bytes_float32(arr_like) -> Optional[bytes]:
    if arr_like is None:
        return None
    try:
        return np.asarray(arr_like, dtype="float32").tobytes()
    except Exception:
        return None

def insert_dream(
    user_email: str,
    text: str,
    tags: Optional[str],
    sleep_hours: Optional[float],
    sleep_quality: Optional[int],
    motifs: Optional[List[str]],
    archetype: Optional[str],
    reframed: Optional[str],
    emotions: Optional[Dict[str, float]],
    embedding: Optional[List[float] | np.ndarray]
) -> int:
    """
    Insert a single dream row for a specific user.
    NOTE: parameter name `text` is preserved to match existing callers.
    """
    if not (user_email and user_email.strip()):
        raise ValueError("user_email is required for per-user storage.")

    with _engine.begin() as conn:
        conn.execute(
            sa_text("""
            INSERT INTO dreams (
                created_at, user_email, text, tags, sleep_hours, sleep_quality,
                motifs, archetype, reframed, emotions, embedding
            )
            VALUES (
                :created_at, :user_email, :text, :tags, :sleep_hours, :sleep_quality,
                :motifs, :archetype, :reframed, :emotions, :embedding
            )
            """),
            dict(
                created_at=datetime.utcnow().isoformat(timespec="seconds"),
                user_email=user_email.strip().lower(),
                text=(text or "").strip(),
                tags=(tags or "").strip() if tags else None,
                sleep_hours=float(sleep_hours) if sleep_hours is not None else None,
                sleep_quality=int(sleep_quality) if sleep_quality is not None else None,
                motifs=json.dumps(motifs or []),
                archetype=(archetype or "unknown"),
                reframed=(reframed or ""),
                emotions=json.dumps(emotions or {}),
                embedding=_to_bytes_float32(embedding)
            )
        )
        res = conn.execute(sa_text("SELECT last_insert_rowid()"))
        return int(res.scalar_one())

def fetch_dreams_dataframe(user_email: str) -> pd.DataFrame:
    """Return all dreams for a given user (ascending by created_at) as a rich dataframe."""
    if not (user_email and user_email.strip()):
        raise ValueError("user_email is required.")

    with _engine.begin() as conn:
        rows = conn.execute(
            sa_text("""
                SELECT * FROM dreams
                WHERE user_email = :user_email
                ORDER BY created_at ASC
            """),
            dict(user_email=user_email.strip().lower())
        ).mappings().all()

    if not rows:
        return pd.DataFrame()

    def decode(row: Dict[str, Any]) -> Dict[str, Any]:
        emb = None
        if row.get("embedding") is not None:
            try:
                emb = np.frombuffer(row["embedding"], dtype="float32")
            except Exception:
                emb = None

        try:
            emoj = json.loads(row.get("emotions") or "{}")
        except Exception:
            emoj = {}

        try:
            motifs = json.loads(row.get("motifs") or "[]")
        except Exception:
            motifs = []

        text_val = row.get("text") or ""
        preview = (text_val[:120] + "…") if len(text_val) > 120 else text_val
        top_em = max(emoj, key=lambda k: emoj.get(k, 0)) if emoj else "neutral"

        return {
            **row,
            "emotions": emoj,
            "motifs": motifs,
            "embedding": emb,
            "preview": preview,
            "top_emotion": top_em,
        }

    data = [decode(dict(r)) for r in rows]
    df = pd.DataFrame(data)
    return df

def fetch_dream_by_id(user_email: str, dream_id: int) -> Optional[Dict[str, Any]]:
    """Fetch a single dream by id for a given user."""
    with _engine.begin() as conn:
        row = conn.execute(
            sa_text("""
                SELECT * FROM dreams
                WHERE user_email = :user_email AND id = :id
                LIMIT 1
            """),
            dict(user_email=(user_email or "").strip().lower(), id=int(dream_id))
        ).mappings().first()

    if not row:
        return None

    r = dict(row)
    # Decode JSON & embedding for convenience
    try:
        r["emotions"] = json.loads(r.get("emotions") or "{}")
    except Exception:
        r["emotions"] = {}
    try:
        r["motifs"] = json.loads(r.get("motifs") or "[]")
    except Exception:
        r["motifs"] = []
    try:
        if r.get("embedding") is not None:
            r["embedding"] = np.frombuffer(r["embedding"], dtype="float32")
    except Exception:
        r["embedding"] = None
    return r

def wipe_user_data(user_email: str) -> None:
    """Delete all dreams for a given user."""
    if not (user_email and user_email.strip()):
        return
    with _engine.begin() as conn:
        conn.execute(
            sa_text("DELETE FROM dreams WHERE user_email = :user_email"),
            dict(user_email=user_email.strip().lower())
        )

def wipe_all_data() -> None:
    """Danger: clears the entire dreams table for all users."""
    with _engine.begin() as conn:
        conn.execute(sa_text("DELETE FROM dreams"))
