import streamlit as st
import pandas as pd
from modules.nlp import get_embedding, ensure_nltk
from modules.llm import analyze_dream_llm
from modules.storage import insert_dream
from modules.visuals import render_emotion_bar

st.title("📘 Log a Dream")
ensure_nltk()

with st.form("log_form", clear_on_submit=False):
    text = st.text_area("Describe your dream in detail", height=220, placeholder="I was running through a maze...")
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

    # sanity fix for emotions to avoid NaN% issues
    emo = llm_out["emotions"]
    total = sum(max(v, 0) for v in emo.values())
    if total <= 0:
        # fallback: neutral 100
        emo = {k: (100.0 if k == "neutral" else 0.0) for k in ["joy","sadness","fear","anger","disgust","surprise","neutral"]}
    else:
        emo = {k: round((max(v, 0)/total)*100.0, 2) for k,v in emo.items()}

    dream_id = insert_dream(
        text=text,
        tags=tags,
        sleep_hours=float(sleep_hours),
        sleep_quality=int(sleep_quality),
        motifs=llm_out["motifs"],
        archetype=llm_out["archetype"],
        reframed=llm_out["reframed"],
        emotions=emo,
        embedding=emb
    )

    st.success("Dream analyzed and saved!")
    st.subheader("Quick insight")
    col1, col2 = st.columns([1,1])
    with col1:
        st.write("**Archetype:**", llm_out["archetype"])
        st.write("**Motifs:**", ", ".join(llm_out["motifs"]) if llm_out["motifs"] else "—")
    with col2:
        render_emotion_bar(emo)

    with st.expander("Therapeutic reframing"):
        st.write(llm_out["reframed"])

    st.caption(f"Saved as ID: {dream_id}")
