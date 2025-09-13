import numpy as np
import nltk
from sentence_transformers import SentenceTransformer
from typing import List, Dict

_model_cache = None

def ensure_nltk():
    try:
        nltk.data.find("tokenizers/punkt")
    except LookupError:
        nltk.download("punkt")

def _emb_model():
    global _model_cache
    if _model_cache is None:
        _model_cache = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    return _model_cache

def get_embedding(text: str) -> np.ndarray:
    m = _emb_model()
    vec = m.encode([text], normalize_embeddings=True)
    return vec[0]

def cosine_sim_matrix(X: np.ndarray) -> np.ndarray:
    Xn = X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-9)
    return Xn @ Xn.T

def dominant_emotion(emo: Dict[str, float]) -> str:
    if not emo:
        return "neutral"
    return max(emo.items(), key=lambda x: x[1])[0]

def group_by_top_emotion(records: List[Dict]):
    d = {}
    for r in records:
        top = dominant_emotion(r.get("emotions", {}))
        d.setdefault(top, []).append(r)
    return d
