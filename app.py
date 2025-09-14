import streamlit as st
from modules.storage import init_db

st.set_page_config(
    page_title="NoctiMind",
    page_icon="🧠",
    layout="wide"
)
init_db()

st.title("🧠 Unlock the Secrets of Your Dreams")
st.write(
    "Discover hidden patterns, emotions, and archetypal meanings in your dreams "
    "with AI-powered analysis and interactive visualizations that reveal your subconscious."
)

# CTA buttons using Streamlit’s built-in navigation
col1, col2 = st.columns(2)
with col1:
    st.page_link("pages/1_📘_Log_a_Dream.py", label="Start Analyzing Dreams →", icon="✨")
with col2:
    st.page_link("pages/2_📊_History.py", label="View Dream History", icon="📚")

st.divider()

# Features section
col1, col2, col3 = st.columns(3)
with col1:
    st.subheader("🧠 AI-Powered Analysis")
    st.write("Extract motifs, archetypes, and emotion intensities from your dream text with Groq + embeddings.")

with col2:
    st.subheader("📈 Beautiful Visualizations")
    st.write("Emotion arcs, motif clouds, and an interactive emotion map that highlights your strongest feelings.")

with col3:
    st.subheader("⏱️ Dream Tracking")
    st.write("Browse history cards, open per-dream insights, and compare clusters over time.")
