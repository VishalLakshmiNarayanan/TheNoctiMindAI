# modules/llm.py
import os
import json
import requests
import streamlit as st
from dotenv import load_dotenv

# Load .env for local dev
load_dotenv()

_API_URL = "https://api.groq.com/openai/v1/chat/completions"

_SYSTEM = (
    "You are NoctiMind, a careful dream analyst. "
    "Return strict JSON. Emotions are percentages that sum to ~100. "
    "Allowed emotions: joy, sadness, fear, anger, disgust, surprise, neutral."
)

# NOTE: double-brace {{ }} any literal braces to avoid KeyError in .format(...)
_USER_TEMPLATE = """
Analyze this dream:
---
{dream}
---

Return JSON with keys:
- motifs: string[] (2-5 concise motif labels)
- archetype: string (one concise archetype, e.g., 'chase/fear', 'falling/loss', 'exam/anxiety', 'social/evaluation', 'travel/transition')
- emotions: object mapping of {{joy,sadness,fear,anger,disgust,surprise,neutral}} to percentages (floats)
- reframed: short calming reframe of the dream (2-4 sentences)
"""

def _safe_get_secret(key: str):
    """Return st.secrets[key] if it exists; do not crash when secrets.toml is missing."""
    try:
        if hasattr(st, "secrets") and key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return None

def _get_groq_key() -> str | None:
    # Prefer Streamlit secrets if configured, else .env / environment
    val = _safe_get_secret("GROQ_API_KEY")
    if val:
        return val
    return os.environ.get("GROQ_API_KEY")

def _get_groq_model() -> str:
    val = _safe_get_secret("GROQ_MODEL")
    if val:
        return val
    return os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")

def _call_groq(messages, temperature=0.2):
    api_key = _get_groq_key()
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY not found. Put it in a .env file (GROQ_API_KEY=...) "
            "or .streamlit/secrets.toml."
        )
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": _get_groq_model(),
        "messages": messages,
        "temperature": temperature,
    }
    r = requests.post(_API_URL, headers=headers, json=payload, timeout=60)
    r.raise_for_status()
    data = r.json()
    return data["choices"][0]["message"]["content"]

def analyze_dream_llm(dream_text: str):
    content = _call_groq([
        {"role": "system", "content": _SYSTEM},
        {"role": "user", "content": _USER_TEMPLATE.format(dream=dream_text)}
    ])

    # Extract JSON if the model wrapped it in text
    start = content.find("{")
    end = content.rfind("}")
    if start != -1 and end != -1 and end > start:
        content = content[start:end+1]

    try:
        obj = json.loads(content)
    except Exception:
        # Safe fallback
        obj = {
            "motifs": [],
            "archetype": "unknown",
            "emotions": {"joy":0,"sadness":0,"fear":0,"anger":0,"disgust":0,"surprise":0,"neutral":100},
            "reframed": "Imagine a calmer version of this story where you feel safe and supported."
        }

    obj.setdefault("motifs", [])
    obj.setdefault("archetype", "unknown")
    obj.setdefault("emotions", {})
    for k in ["joy","sadness","fear","anger","disgust","surprise","neutral"]:
        obj["emotions"][k] = float(obj["emotions"].get(k, 0))
    obj.setdefault("reframed", "")
    return obj
