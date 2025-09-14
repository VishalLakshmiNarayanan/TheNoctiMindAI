# components/ui.py
from __future__ import annotations
import streamlit as st
from modules.auth import user_greeting, logout_button

def render_top_nav(hide_sidebar: bool = True):
    """Draw a pill-style top navbar with page links + user info on the right."""
    # Global CSS (navbar + optional hide sidebar)
    st.markdown(f"""
    <style>
    {"[data-testid='stSidebar'],[data-testid='stSidebarNav']{{display:none;}}" if hide_sidebar else ""}
    .main .block-container {{ padding-top: 1.2rem; }}

    .navbar {{
      display:flex; gap:.5rem; align-items:center; padding:.6rem; margin-bottom:.75rem;
      background: rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,.08);
      border-radius: 12px;
    }}
    .navpill {{
      display:inline-flex; align-items:center; gap:.5rem;
      padding:.5rem .8rem; border-radius:999px;
      border:1px solid rgba(255,255,255,.12);
      background: rgba(255,255,255,.02); color:#e6e6ef; text-decoration:none;
      font-weight:600; font-size:.95rem;
    }}
    .navpill:hover {{ background: rgba(255,255,255,.06); border-color: rgba(255,255,255,.2); }}
    </style>
    """, unsafe_allow_html=True)

    # Layout row
    st.markdown('<div class="navbar">', unsafe_allow_html=True)
    c1, c2, c3, c4, cspacer, cr = st.columns([1.2,1.1,1.1,1.1,1,2], gap="small")

    with c1:
        st.page_link("pages/1_📘_Log_a_Dream.py", label="📘 Log a Dream", use_container_width=True)
    with c2:
        st.page_link("pages/2_📊_History.py", label="📊 History", use_container_width=True)
    with c3:
        st.page_link("pages/3_🧭_Insights.py", label="🧭 Insights", use_container_width=True)
    with c4:
        st.page_link("pages/4_⚙️_Settings.py", label="⚙️ Settings", use_container_width=True)
    with cr:
        user_greeting()
        logout_button()

    st.markdown('</div>', unsafe_allow_html=True)
