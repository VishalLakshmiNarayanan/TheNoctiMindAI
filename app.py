# app.py
from __future__ import annotations
import streamlit as st
import pandas as pd

from modules.storage import init_db, fetch_dreams_dataframe
from modules.auth import (
    ensure_session_keys, current_user,
    login_form, signup_form, logout_button, user_greeting
)

# shadcn helpers
from components.shad_theme import use_page, header, nav_tabs, kpi_card, card

# ---------- Page / DB / Auth ----------
use_page("NoctiMind", hide_sidebar=True)   # call ONCE
init_db()
ensure_session_keys()
user = current_user()

# Sign-in gate
if not user:
    st.title("🧠 Welcome to NoctiMind")
    st.write("Sign in or create an account to unlock the secrets of your dreams.")
    mode = st.segmented_control("Mode", options=["Sign In", "Sign Up"], default="Sign In")
    if mode == "Sign In":
        login_form()
    else:
        signup_form()
    st.stop()

# ---------- Header + Tabs (shadcn style) ----------
header()
nav_tabs("Home")   # don't assign; it navigates internally

# Right-aligned user block
_, right = st.columns([0.7, 0.3])
with right:
    user_greeting()
    logout_button()

# ---------- Overview content ----------
st.markdown("#### Overview")

df = fetch_dreams_dataframe(user["email"])
total_dreams = int(df.shape[0]) if not df.empty else 0
avg_sleep = (
    f"{df['sleep_hours'].dropna().mean():.1f} h"
    if (not df.empty and 'sleep_hours' in df)
    else "–"
)
trend = "↑ improving" if total_dreams >= 2 else "–"

# KPI row
c1, c2, c3 = st.columns(3)
kpi_card("Dreams Logged", f"{total_dreams:,}", "+ recent activity", col=c1)
kpi_card("Avg Sleep", f"{avg_sleep}", "+ consistency helps", col=c2)
kpi_card("Mood Trend", trend, "+ gentle routines", col=c3)

# Monthly bar chart card
def _monthly_chart():
    if df.empty:
        st.info("Log your first dream to see charts here.")
        return
    d = df.copy()
    d["month"] = pd.to_datetime(d["created_at"]).dt.to_period("M").astype(str)
    counts = d.groupby("month").size().reset_index(name="count")
    st.bar_chart(counts.set_index("month")["count"])

card("Monthly Dreams", _monthly_chart)

# Feature highlights
st.divider()
c1, c2, c3 = st.columns(3)
with c1:
    st.subheader("🧠 AI-Powered Analysis")
    st.write("Extract motifs, archetypes, and emotion intensities from your dream text with Groq + embeddings.")
with c2:
    st.subheader("📈 Beautiful Visualizations")
    st.write("Emotion arcs, motif clouds, and an interactive emotion map highlight your strongest feelings.")
with c3:
    st.subheader("⏱️ Dream Tracking")
    st.write("Browse history cards, open per-dream insights, and compare clusters over time.")
