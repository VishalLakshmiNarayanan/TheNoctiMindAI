# pages/1_📘_Log_a_Dream.py
from __future__ import annotations

import time
from typing import Optional, Dict

import streamlit as st

# -------- Auth (login required + user info) --------
from modules.auth import require_login, current_user

# -------- NLP / LLM / Embeddings --------
from modules.nlp import get_embedding, ensure_nltk
from modules.llm import analyze_dream_llm

# -------- Storage (per-user) --------
from modules.storage import insert_dream  # expects user_email as first arg (per-user)

# -------- Visuals --------
from modules.visuals import render_emotion_bar, emotion_node_graph

# -------- Voice (optional) --------
from modules.speech import transcribe_audio_bytes

# -------- shadcn helpers --------
from components.shad_theme import use_page, header, nav_tabs, card


# -------------------------- Page Shell --------------------------
use_page("Analyze · NoctiMind", hide_sidebar=True)
require_login("Please sign up or sign in to view this page.")
user = current_user()
if not user:
    st.stop()

header()
nav_tabs("Dream Logs")
      # keep the same tab naming vibe
# (Optional) route on tab:
# if active == "Overview": st.switch_page("app.py")
# if active == "Analytics": st.switch_page("pages/2_📊_History.py")
# if active == "Reports": st.switch_page("pages/3_🧭_Insights.py")

ensure_nltk()

# -------------------------- Helpers --------------------------
def _normalize_emotions(emo: Dict[str, float] | None) -> Dict[str, float]:
    """
    Force a consistent 7-emotion distribution as percentages (0..100, sum≈100).
    Missing keys default to 0, and if total==0 -> neutral=100.
    """
    emo = emo or {}
    keys = ["joy", "sadness", "fear", "anger", "disgust", "surprise", "neutral"]
    total = 0.0
    vals = {}
    for k in keys:
        try:
            v = float(emo.get(k, 0.0))
        except Exception:
            v = 0.0
        vals[k] = max(v, 0.0)
        total += vals[k]

    if total <= 0:
        return {k: (100.0 if k == "neutral" else 0.0) for k in keys}

    return {k: round((vals[k] / total) * 100.0, 2) for k in keys}

def _safe_list(txt_list):
    if not isinstance(txt_list, list):
        return []
    return [str(x) for x in txt_list if isinstance(x, (str, int, float))]

# -------------------------- TYPE CARD --------------------------
def _type_card_body():
    with st.form("log_form_type", clear_on_submit=False):
        text = st.text_area(
            "Describe your dream in detail",
            height=220,
            placeholder="I was walking through a forest when suddenly..."
        )
        c1, c2 = st.columns(2)
        with c1:
            sleep_hours = st.number_input("Sleep hours", min_value=0.0, max_value=24.0, value=7.0, step=0.5)
        with c2:
            sleep_quality = st.slider("Sleep quality (1=poor, 5=great)", 1, 5, 3)

        tags = st.text_input("Optional tags (comma separated)", placeholder="exam, chase, travel")
        submitted = st.form_submit_button("Analyze & Save")

    if not submitted:
        return

    if not text.strip():
        st.error("Please enter your dream text.")
        st.stop()

    # Embedding
    with st.spinner("Embedding dream..."):
        emb = get_embedding(text)

    # LLM pipeline
    with st.spinner("Extracting motifs, emotions, archetype, and reframing (LLM)..."):
        llm_out = analyze_dream_llm(text)

    # Normalize & sanitize
    emo = _normalize_emotions(llm_out.get("emotions", {}))
    motifs = _safe_list(llm_out.get("motifs", []))
    archetype = str(llm_out.get("archetype", "unknown")) or "unknown"
    reframed = str(llm_out.get("reframed", ""))

    # Save (PER-USER: pass user email first)
    _ = insert_dream(
        user_email=user["email"],
        text=text,
        tags=tags,
        sleep_hours=float(sleep_hours),
        sleep_quality=int(sleep_quality),
        motifs=motifs,
        archetype=archetype,
        reframed=reframed,
        emotions=emo,
        embedding=emb
    )

    st.success("Dream analyzed and saved!")
    c1, c2 = st.columns([1, 1])
    with c1:
        st.write("**Archetype:**", archetype)
        st.write("**Motifs:**", ", ".join(motifs) if motifs else "—")
    with c2:
        render_emotion_bar(emo)

    st.subheader("Emotion Map")
    st.plotly_chart(emotion_node_graph(emo), use_container_width=True)

    with st.expander("Therapeutic reframing"):
        st.write(reframed)

card("Analyze & Save (Typing)", _type_card_body)

# -------------------------- VOICE CARD --------------------------
def _voice_card_body():
    st.write("Record a quick voice note or upload an audio file, and I’ll transcribe it into the editor.")

    # Keep transcript in session across reruns
    if "voice_text" not in st.session_state:
        st.session_state.voice_text = ""

    def _set_transcript(val: str):
        st.session_state.voice_text = val or ""

    # A) Microphone recorder (optional component)
    try:
        from streamlit_mic_recorder import mic_recorder
        audio = mic_recorder(
            start_prompt="Start recording",
            stop_prompt="Stop",
            just_once=True,
            use_container_width=True,
            key="mic1",
        )
        if audio and audio.get("bytes"):
            with st.spinner("Transcribing your recording..."):
                t = transcribe_audio_bytes(audio["bytes"], filename="mic.wav")
                _set_transcript(t)
                st.success("Transcription ready. You can edit it below.")
    except Exception:
        st.caption("🎤 Microphone recorder component unavailable. You can still upload a file below.")

    st.divider()

    # B) File uploader
    up = st.file_uploader(
        "Or upload an audio file",
        type=["wav", "mp3", "m4a", "webm"],
        key="uploader1"
    )
    if up is not None:
        raw = up.read()
        if raw:
            with st.spinner("Transcribing your file..."):
                t = transcribe_audio_bytes(raw, filename=up.name)
                _set_transcript(t)
                st.success("Transcription ready. You can edit it below.")

    # C) Edit transcript and analyze
    st.text_area(
        "Transcript",
        key="voice_text",
        height=220,
        placeholder="Your transcript will appear here after recording/upload."
    )

    c1, c2 = st.columns([1, 1])
    with c1:
        v_sleep_hours = st.number_input("Sleep hours", min_value=0.0, max_value=24.0, value=7.0, step=0.5, key="v_hours")
    with c2:
        v_sleep_quality = st.slider("Sleep quality (1=poor, 5=great)", 1, 5, 3, key="v_quality")
    v_tags = st.text_input("Optional tags (comma separated)", placeholder="exam, chase, travel", key="v_tags")

    if st.button("Analyze & Save (from transcript)", type="primary", key="analyze_from_voice"):
        voice_text = (st.session_state.get("voice_text") or "").strip()
        if not voice_text:
            st.error("No transcript text to analyze.")
            st.stop()

        with st.spinner("Embedding transcript..."):
            emb = get_embedding(voice_text)

        with st.spinner("Extracting motifs, emotions, archetype, and reframing (LLM)..."):
            llm_out = analyze_dream_llm(voice_text)

        emo = _normalize_emotions(llm_out.get("emotions", {}))
        motifs = _safe_list(llm_out.get("motifs", []))
        archetype = str(llm_out.get("archetype", "unknown")) or "unknown"
        reframed = str(llm_out.get("reframed", ""))

        _ = insert_dream(
            user_email=user["email"],
            text=voice_text,
            tags=v_tags,
            sleep_hours=float(v_sleep_hours),
            sleep_quality=int(v_sleep_quality),
            motifs=motifs,
            archetype=archetype,
            reframed=reframed,
            emotions=emo,
            embedding=emb
        )

        st.success("Dream analyzed and saved!")
        c1, c2 = st.columns([1, 1])
        with c1:
            st.write("**Archetype:**", archetype)
            st.write("**Motifs:**", ", ".join(motifs) if motifs else "—")
        with c2:
            render_emotion_bar(emo)

        st.subheader("Emotion Map")
        st.plotly_chart(emotion_node_graph(emo), use_container_width=True)

        with st.expander("Therapeutic reframing"):
            st.write(reframed)

card("Analyze & Save (Voice)", _voice_card_body)
