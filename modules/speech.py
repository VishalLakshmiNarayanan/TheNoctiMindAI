# modules/speech.py
import os
import io
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# Groq OpenAI-compatible transcription endpoint
_GROQ_AUDIO_URL = "https://api.groq.com/openai/v1/audio/transcriptions"

def _safe_get_secret(key: str):
    try:
        if hasattr(st, "secrets") and key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return None

def _get_groq_key():
    return _safe_get_secret("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")

def _get_stt_model():
    # default to whisper-large-v3 (you can change in .env or secrets)
    return _safe_get_secret("GROQ_STT_MODEL") or os.environ.get("GROQ_STT_MODEL", "whisper-large-v3")

def transcribe_audio_bytes(audio_bytes: bytes, filename: str = "audio.wav", response_format: str = "text") -> str:
    """
    Send raw audio bytes to Groq Whisper endpoint and return the transcript (str).
    Supported formats: wav, mp3, m4a, webm, etc.
    """
    api_key = _get_groq_key()
    if not api_key:
        raise RuntimeError("GROQ_API_KEY not found for transcription.")

    files = {
        "file": (filename, io.BytesIO(audio_bytes), "application/octet-stream"),
    }
    data = {
        "model": _get_stt_model(),
        "response_format": response_format,  # "text" -> plain string back
        # You can add "temperature": 0 here if desired
    }
    headers = {"Authorization": f"Bearer {api_key}"}

    resp = requests.post(_GROQ_AUDIO_URL, headers=headers, files=files, data=data, timeout=120)
    resp.raise_for_status()
    # For response_format="text" the body is the transcript string
    return resp.text.strip()
