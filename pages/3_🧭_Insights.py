# pages/3_🧭_Insights.py
from __future__ import annotations

import streamlit as st
import pandas as pd
import numpy as np

# Auth
from modules.auth import require_login, current_user

# Storage & visuals
from modules.storage import fetch_dreams_dataframe
from modules.visuals import correlation_scatter, emotion_distribution_pie

# shadcn helpers
from components.shad_theme import use_page, header, nav_tabs, card



# -------------------------- Page shell --------------------------
use_page("Insights · NoctiMind", hide_sidebar=True)
require_login("Please sign up or sign in to view this page.")
user = current_user()
if not user:
    st.stop()

header()
nav_tabs("Dream Insights")

# (Optional routing)
# if active == "Overview": st.switch_page("app.py")
# if active == "Analytics": st.switch_page("pages/2_📊_History.py")
# if active == "Notifications": st.switch_page("pages/1_📘_Log_a_Dream.py")

# -------------------------- Data --------------------------
df = fetch_dreams_dataframe(user["email"])
if df.empty:
    st.info("Log a dream to see insights.")
    st.stop()

# Ensure 'emotions' is a dict per row (defensive)
def _ensure_emodict(val):
    return val if isinstance(val, dict) else {}

df["emotions"] = df["emotions"].apply(_ensure_emodict)

# Negative affect (percent scale)
df["neg_affect"] = df.apply(
    lambda r: float(r["emotions"].get("fear", 0))
            + float(r["emotions"].get("sadness", 0))
            + float(r["emotions"].get("anger", 0))
            + float(r["emotions"].get("disgust", 0)),
    axis=1
)

# Numeric safety
for col in ("sleep_hours", "sleep_quality", "neg_affect"):
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# -------------------------- Emotion Distribution (card) --------------------------
def _emotion_dist():
    # Build an average emotion distribution dict across all dreams
    keys = ["joy","sadness","fear","anger","disgust","surprise","neutral"]
    sums = {k: 0.0 for k in keys}
    n = 0
    for em in df["emotions"]:
        if isinstance(em, dict):
            for k in keys:
                sums[k] += float(em.get(k, 0.0))
            n += 1
    avg = {k: round(sums[k] / n, 2) if n else (100.0 if k == "neutral" else 0.0) for k in keys}
    st.plotly_chart(emotion_distribution_pie(avg), use_container_width=True)

card("Emotion Distribution", _emotion_dist)

# -------------------------- Correlations (card) --------------------------
def _correlations():
    c1, c2 = st.columns(2)
    with c1:
        d = df.dropna(subset=["sleep_hours", "neg_affect"])
        if d.empty:
            st.info("Need sleep hours + emotions to plot this.")
        else:
            st.plotly_chart(
                correlation_scatter(
                    d, x="sleep_hours", y="neg_affect",
                    title="Sleep Hours vs Negative Affect"
                ),
                use_container_width=True
            )
    with c2:
        d = df.dropna(subset=["sleep_quality", "neg_affect"])
        if d.empty:
            st.info("Need sleep quality + emotions to plot this.")
        else:
            st.plotly_chart(
                correlation_scatter(
                    d, x="sleep_quality", y="neg_affect",
                    title="Sleep Quality vs Negative Affect"
                ),
                use_container_width=True
            )

card("Sleep vs Negative Affect", _correlations)

# -------------------------- Personalized feedback (card) --------------------------
def _feedback():
    n_samples = len(df)
    if n_samples < 3:
        st.info("Add at least 3 dreams to see trend-based feedback.")
        return

    max_n = int(min(30, n_samples))
    default_n = int(min(10, n_samples))
    min_n = 3

    if max_n <= min_n:
        last_n = max_n
        st.caption(f"Analyzing last {last_n} dreams.")
    else:
        last_n = st.slider("Analyze last N dreams", min_value=min_n, max_value=max_n, value=default_n)

    df_sorted = df.sort_values("created_at", ascending=True)
    recent = df_sorted.tail(int(last_n))
    avg_neg = float(recent["neg_affect"].mean()) if not recent.empty else 0.0

    if avg_neg >= 50:
        st.warning(
            "You've had a run of **fear/sadness/anger** leaning dreams. "
            "Try winding down earlier, reduce late screens, or do a brief pre-sleep journaling session."
        )
    elif avg_neg >= 25:
        st.info(
            "Mixed emotional tone lately. Light relaxation before bed and consistent sleep times "
            "may tilt dreams positively."
        )
    else:
        st.success(
            "Your recent dreams skew calmer/neutral. Keep steady routines and hydration; "
            "you're on a good trend!"
        )

card("Personalized Feedback", _feedback)
