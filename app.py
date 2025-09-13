import streamlit as st
from modules.storage import init_db

st.set_page_config(
    page_title="NoctiMind",
    page_icon="🧠",
    layout="wide"
)

# Ensure DB exists/migrated
init_db()

st.title("🧠 NoctiMind")
st.caption("Dreams → Insights. Log, analyze, and reflect.")

st.markdown("""
**What you can do:**
- Log a dream, add sleep quality & hours.
- Get AI-powered motifs, emotions, and a calm reframing.
- See history, similarity groups, emotion arcs, and archetypes.
- View correlations between dreams and sleep metrics.
""")

st.page_link("pages/1_📘_Log_a_Dream.py", label="📘 Log a Dream", icon="📝")
st.page_link("pages/2_📊_History.py", label="📊 History & Similarity", icon="📚")
st.page_link("pages/3_🧭_Insights.py", label="🧭 Insights", icon="💡")
st.page_link("pages/4_⚙️_Settings.py", label="⚙️ Settings", icon="⚙️")
