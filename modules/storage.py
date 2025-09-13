from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
import json
import pandas as pd
import numpy as np
from datetime import datetime

_DB_PATH = "sqlite:///noctimind.db"

_engine = create_engine(
    _DB_PATH,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

def init_db():
    with _engine.begin() as conn:
        conn.execute(text("""
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

def insert_dream(text, tags, sleep_hours, sleep_quality, motifs, archetype, reframed, emotions, embedding):
    with _engine.begin() as conn:
        conn.execute(
            text("""
            INSERT INTO dreams (created_at, text, tags, sleep_hours, sleep_quality, motifs, archetype, reframed, emotions, embedding)
            VALUES (:created_at, :text, :tags, :sleep_hours, :sleep_quality, :motifs, :archetype, :reframed, :emotions, :embedding)
            """),
            dict(
                created_at=datetime.utcnow().isoformat(timespec="seconds"),
                text=text.strip(),
                tags=(tags or "").strip(),
                sleep_hours=float(sleep_hours) if sleep_hours is not None else None,
                sleep_quality=int(sleep_quality) if sleep_quality is not None else None,
                motifs=json.dumps(motifs or []),
                archetype=archetype or "unknown",
                reframed=reframed or "",
                emotions=json.dumps(emotions or {}),
                embedding=np.asarray(embedding, dtype="float32").tobytes()
            )
        )
        # fetch last id
        res = conn.execute(text("SELECT last_insert_rowid()"))
        return res.scalar_one()

def fetch_dreams_dataframe() -> pd.DataFrame:
    with _engine.begin() as conn:
        rows = conn.execute(text("SELECT * FROM dreams ORDER BY created_at ASC")).mappings().all()
    if not rows:
        return pd.DataFrame()

    def decode(row):
        import numpy as np, json, struct
        emb = np.frombuffer(row["embedding"], dtype="float32")
        emoj = json.loads(row["emotions"] or "{}")
        motifs = json.loads(row["motifs"] or "[]")
        preview = (row["text"][:120] + "…") if len(row["text"]) > 120 else row["text"]
        # determine top emotion
        top_em = max(emoj, key=lambda k: emoj.get(k,0)) if emoj else "neutral"
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

def wipe_all_data():
    with _engine.begin() as conn:
        conn.execute(text("DELETE FROM dreams"))
