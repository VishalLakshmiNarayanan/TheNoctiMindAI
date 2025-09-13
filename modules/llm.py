import os
import json
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

def _get_groq_key():
    # Prefer Streamlit secrets, fallback to env
    key = st.secrets.get("GROQ_API_KEY", None) if hasattr(st, "secrets") else None
    return key or os.environ.get("GROQ_API_KEY")

def _get_groq_model():
    m = st.secrets.get("GROQ_MODEL", None) if hasattr(st, "secrets") else None
    return m or os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")

_API_URL = "https://api.groq.com/openai/v1/chat/completions"

_SYSTEM = (
"You are NoctiMind, a careful dream analyst. "
"Return strict JSON. Emotions are percentages that sum to ~100. "
"Allowed emotions: joy, sadness, fear, anger, disgust, surprise, neutral."
)

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

def _call_groq(messages, temperature=0.2):
    api_key = _get_groq_key()
    if not api_key:
        raise RuntimeError("GROQ_API_KEY not set in secrets or environment.")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    model = _get_groq_model()
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
    }
    r = requests.post(_API_URL, headers=headers, json=payload, timeout=60)
    r.raise_for_status()
    data = r.json()
    # OpenAI-compatible shape
    content = data["choices"][0]["message"]["content"]
    return content

def analyze_dream_llm(dream_text: str):
    content = _call_groq([
        {"role": "system", "content": _SYSTEM},
        {"role": "user", "content": _USER_TEMPLATE.format(dream=dream_text)}
    ])
    # Try parse JSON anywhere in content
    # Some models wrap JSON with text; extract best-effort
    start = content.find("{")
    end = content.rfind("}")
    if start != -1 and end != -1 and end > start:
        content = content[start:end+1]
    try:
        obj = json.loads(content)
    except Exception:
        # fallback minimal structure
        obj = {
            "motifs": [],
            "archetype": "unknown",
            "emotions": {"joy":0,"sadness":0,"fear":0,"anger":0,"disgust":0,"surprise":0,"neutral":100},
            "reframed": "Imagine a calmer version of this story where you feel safe and supported."
        }

    # Patch keys
    obj.setdefault("motifs", [])
    obj.setdefault("archetype", "unknown")
    obj.setdefault("emotions", {})
    for k in ["joy","sadness","fear","anger","disgust","surprise","neutral"]:
        obj["emotions"][k] = float(obj["emotions"].get(k, 0))

    obj.setdefault("reframed", "")
    return obj
