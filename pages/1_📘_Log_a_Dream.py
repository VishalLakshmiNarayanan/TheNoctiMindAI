import streamlit as st
from modules.nlp import get_embedding, ensure_nltk
from modules.llm import analyze_dream_llm
from modules.storage import insert_dream
from modules.visuals import render_emotion_bar, emotion_node_graph

# NEW: voice imports (optional)
from modules.speech import transcribe_audio_bytes
from typing import Optional

st.title("📘 Analyze a Dream")
ensure_nltk()

def _normalize_emotions(emo: dict) -> dict:
    keys = ["joy","sadness","fear","anger","disgust","surprise","neutral"]
    total = sum(max(float(emo.get(k, 0)), 0.0) for k in keys)
    if total <= 0:
        return {k: (100.0 if k == "neutral" else 0.0) for k in keys}
    return {k: round((max(float(emo.get(k, 0.0)), 0.0) / total) * 100.0, 2) for k in keys}

tab_type, tab_voice = st.tabs(["⌨️ Type", "🎙 Voice"])

# ---- TYPE TAB ----
with tab_type:
    with st.form("log_form_type", clear_on_submit=False):
        text = st.text_area("Describe your dream in detail", height=220, placeholder="I was walking through a forest when suddenly...")
        sleep_hours = st.number_input("Sleep hours", min_value=0.0, max_value=24.0, value=7.0, step=0.5)
        sleep_quality = st.slider("Sleep quality (1=poor, 5=great)", 1, 5, 3)
        tags = st.text_input("Optional tags (comma separated)", placeholder="exam, chase, travel")
        submitted = st.form_submit_button("Analyze & Save")

    if submitted:
        if not text.strip():
            st.error("Please enter your dream text.")
            st.stop()

        with st.spinner("Embedding dream..."):
            emb = get_embedding(text)

        with st.spinner("Extracting motifs, emotions, archetype, and reframing (LLM)..."):
            llm_out = analyze_dream_llm(text)

        emo = _normalize_emotions(llm_out["emotions"])

        dream_id = insert_dream(
            text=text, tags=tags, sleep_hours=float(sleep_hours), sleep_quality=int(sleep_quality),
            motifs=llm_out["motifs"], archetype=llm_out["archetype"], reframed=llm_out["reframed"],
            emotions=emo, embedding=emb
        )

        st.success("Dream analyzed and saved!")
        st.subheader("Quick insight")
        c1, c2 = st.columns([1,1])
        with c1:
            st.write("**Archetype:**", llm_out["archetype"])
            st.write("**Motifs:**", ", ".join(llm_out["motifs"]) if llm_out["motifs"] else "—")
        with c2:
            render_emotion_bar(emo)

        st.subheader("Emotion Map")
        st.plotly_chart(emotion_node_graph(emo), use_container_width=True)

        with st.expander("Therapeutic reframing"):
            st.write(llm_out["reframed"])

# ---- VOICE TAB ----
with tab_voice:
    st.write("Record a quick voice note or upload an audio file, and I’ll transcribe it into the editor.")

    # --- Session-state setup for transcript ---
    if "voice_text" not in st.session_state:
        st.session_state.voice_text = ""  # what the text_area shows/edits

    # helper to update transcript (works across reruns)
    def _set_transcript(text: str):
        st.session_state.voice_text = text or ""

    # --- A) Microphone recorder (optional component) ---
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

    # --- B) File uploader (wav/mp3/m4a/webm) ---
    up = st.file_uploader("Or upload an audio file", type=["wav", "mp3", "m4a", "webm"], key="uploader1")
    if up is not None:
        raw = up.read()
        if raw:
            with st.spinner("Transcribing your file..."):
                t = transcribe_audio_bytes(raw, filename=up.name)
                _set_transcript(t)
                st.success("Transcription ready. You can edit it below.")

    # --- C) Edit transcript and analyze ---
    st.text_area(
        "Transcript",
        key="voice_text",               # bind to session_state
        height=220,
        placeholder="Your transcript will appear here after recording/upload."
    )

    colA, colB = st.columns([1,1])
    with colA:
        v_sleep_hours = st.number_input("Sleep hours", min_value=0.0, max_value=24.0, value=7.0, step=0.5, key="v_hours")
    with colB:
        v_sleep_quality = st.slider("Sleep quality (1=poor, 5=great)", 1, 5, 3, key="v_quality")
    v_tags = st.text_input("Optional tags (comma separated)", placeholder="exam, chase, travel", key="v_tags")

    if st.button("Analyze & Save (from transcript)", type="primary", use_container_width=False, key="analyze_from_voice"):
        voice_text = (st.session_state.get("voice_text") or "").strip()
        if not voice_text:
            st.error("No transcript text to analyze.")
            st.stop()

        with st.spinner("Embedding transcript..."):
            emb = get_embedding(voice_text)

        with st.spinner("Extracting motifs, emotions, archetype, and reframing (LLM)..."):
            llm_out = analyze_dream_llm(voice_text)

        # normalize emotions (reuse your helper if defined)
        keys = ["joy","sadness","fear","anger","disgust","surprise","neutral"]
        emo_raw = llm_out.get("emotions", {})
        total = sum(max(float(emo_raw.get(k, 0.0)), 0.0) for k in keys)
        if total <= 0:
            emo = {k: (100.0 if k == "neutral" else 0.0) for k in keys}
        else:
            emo = {k: round((max(float(emo_raw.get(k, 0.0)), 0.0) / total) * 100.0, 2) for k in keys}

        dream_id = insert_dream(
            text=voice_text, tags=v_tags, sleep_hours=float(v_sleep_hours), sleep_quality=int(v_sleep_quality),
            motifs=llm_out.get("motifs", []), archetype=llm_out.get("archetype", "unknown"),
            reframed=llm_out.get("reframed", ""),
            emotions=emo, embedding=emb
        )

        st.success("Dream analyzed and saved!")
        c1, c2 = st.columns([1,1])
        with c1:
            st.write("**Archetype:**", llm_out.get("archetype", "unknown"))
            st.write("**Motifs:**", ", ".join(llm_out.get("motifs", [])) or "—")
        with c2:
            render_emotion_bar(emo)

        st.subheader("Emotion Map")
        st.plotly_chart(emotion_node_graph(emo), use_container_width=True)

        with st.expander("Therapeutic reframing"):
            st.write(llm_out.get("reframed", ""))
