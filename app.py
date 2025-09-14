# app.py
from __future__ import annotations
import streamlit as st
from modules.storage import init_db
from modules.auth import (
    ensure_session_keys, current_user,
    login_form, signup_form, logout_button, user_greeting
)

st.set_page_config(
    page_title="NoctiMind",
    page_icon="🧠",
    layout="wide"
)

# ------------- Settings -------------
HIDE_SIDEBAR = True   # set False if you want to keep the sidebar visible

# ------------- Global CSS (navbar + optional sidebar hide) -------------
st.markdown("""
<style>
/* Optional: hide sidebar and the collapse button */
%s
/* Top nav container */
.navbar {
  display:flex; gap:.5rem; align-items:center; padding:.6rem; margin-bottom:.75rem;
  background: rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,.08);
  border-radius: 12px;
}
/* Nav pill */
.navpill {
  display:inline-flex; align-items:center; gap:.5rem;
  padding: .5rem .8rem; border-radius: 999px;
  border:1px solid rgba(255,255,255,.12);
  background: rgba(255,255,255,.02); color: #e6e6ef; text-decoration:none;
  font-weight: 600; font-size: 0.95rem;
}
.navpill:hover { background: rgba(255,255,255,.06); border-color: rgba(255,255,255,.2); }
.navpill span.emoji { filter: drop-shadow(0 0 0 transparent); }
</style>
""" % ("""
/* hide sidebar entirely */
[data-testid="stSidebar"] { display:none; }
[data-testid="stSidebarNav"] { display:none; }
[data-testid="stToolbar"] button[kind="header"] { display:none; }  /* optional hamburger */
.main .block-container { padding-top: 1.2rem; }
""" if HIDE_SIDEBAR else ""), unsafe_allow_html=True)

# ------------- DB + Auth -------------
init_db()
ensure_session_keys()
user = current_user()

if not user:
    st.title("🧠 Welcome to NoctiMind")
    st.write("Sign in or create an account to unlock the secrets of your dreams.")
    mode = st.segmented_control("Mode", options=["Sign In", "Sign Up"], default="Sign In")
    if mode == "Sign In":
        login_form()
    else:
        signup_form()
    st.stop()

# ------------- Top Navbar -------------
with st.container():
    st.markdown('<div class="navbar">', unsafe_allow_html=True)
    col1, col2, col3, col4, col5 = st.columns([1.3,1.2,1.1,1.1,3], gap="small")

    with col1:
        st.page_link("pages/1_📘_Log_a_Dream.py", label="📘 Log a Dream", use_container_width=True)
    with col2:
        st.page_link("pages/2_📊_History.py", label="📊 History", use_container_width=True)
    with col3:
        st.page_link("pages/3_🧭_Insights.py", label="🧭 Insights", use_container_width=True)
    with col4:
        st.page_link("pages/4_⚙️_Settings.py", label="⚙️ Settings", use_container_width=True)
    with col5:
        # Right-aligned user info & logout
        user_greeting()
        logout_button()
    st.markdown('</div>', unsafe_allow_html=True)

# ------------- Landing Content -------------
st.title("🧠 Unlock the Secrets of Your Dreams")
st.write(
    "Discover hidden patterns, emotions, and archetypal meanings in your dreams "
    "with AI-powered analysis and interactive visualizations that reveal your subconscious."
)

st.divider()

# Features section
c1, c2, c3 = st.columns(3)
with c1:
    st.subheader("🧠 AI-Powered Analysis")
    st.write("Extract motifs, archetypes, and emotion intensities from your dream text with Groq + embeddings.")
with c2:
    st.subheader("📈 Beautiful Visualizations")
    st.write("Emotion arcs, motif clouds, and an interactive emotion map that highlights your strongest feelings.")
with c3:
    st.subheader("⏱️ Dream Tracking")
    st.write("Browse history cards, open per-dream insights, and compare clusters over time.")
