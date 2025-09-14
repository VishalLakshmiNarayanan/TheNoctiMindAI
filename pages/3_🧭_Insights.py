# pages/3_🧭_Insights.py
from __future__ import annotations

import streamlit as st
import pandas as pd
import numpy as np

# Auth & nav
from modules.auth import require_login, current_user
require_login("Please sign up or sign in to view this page.")
from components.ui import render_top_nav
render_top_nav(hide_sidebar=True)

# Storage & visuals
from modules.storage import fetch_dreams_dataframe
from modules.visuals import correlation_scatter, emotion_distribution_pie

# ---------- Page ----------
user = current_user() 
if not user:
    st.stop() # {'email': ..., 'name': ...}
st.title("🧭 Insights")

# Pull only THIS user's dreams
df = fetch_dreams_dataframe(user["email"])
if df.empty:
    st.info("Log a dream to see insights.")
    st.stop()

# Ensure 'emotions' is a dict per row (defensive)
def _ensure_emodict(val):
    return val if isinstance(val, dict) else {}
df["emotions"] = df["emotions"].apply(_ensure_emodict)

st.subheader("Emotion distribution")
st.plotly_chart(emotion_distribution_pie(df), use_container_width=True)

st.subheader("Sleep vs. Negative Affect")
# Negative affect = fear + sadness + anger + disgust (values already normalized to %)
df["neg_affect"] = df.apply(
    lambda r: float(r["emotions"].get("fear", 0))
            + float(r["emotions"].get("sadness", 0))
            + float(r["emotions"].get("anger", 0))
            + float(r["emotions"].get("disgust", 0)),
    axis=1
)

# Safer numeric columns (avoid NaNs in scatter)
for col in ("sleep_hours", "sleep_quality", "neg_affect"):
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(
        correlation_scatter(df.dropna(subset=["sleep_hours", "neg_affect"]),
                            x="sleep_hours", y="neg_affect",
                            title="Sleep Hours vs Negative Affect"),
        use_container_width=True
    )
with col2:
    st.plotly_chart(
        correlation_scatter(df.dropna(subset=["sleep_quality", "neg_affect"]),
                            x="sleep_quality", y="neg_affect",
                            title="Sleep Quality vs Negative Affect"),
        use_container_width=True
    )

# --- Personalized feedback ---
st.subheader("Personalized feedback")

n_samples = len(df)
if n_samples < 3:
    st.info("Add at least 3 dreams to see trend-based feedback.")
else:
    max_n = int(min(30, n_samples))
    default_n = int(min(10, n_samples))
    min_n = 3

    # Ensure valid bounds: if max_n <= min_n, auto-select
    if max_n <= min_n:
        last_n = max_n
        st.caption(f"Analyzing last {last_n} dreams.")
    else:
        last_n = st.slider("Analyze last N dreams", min_value=min_n, max_value=max_n, value=default_n)

    # Use chronological order, then take the tail
    df_sorted = df.sort_values("created_at", ascending=True)
    recent = df_sorted.tail(int(last_n))
    avg_neg = recent["neg_affect"].mean() if not recent.empty else 0.0

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
