import streamlit as st
import pandas as pd
import numpy as np
from modules.storage import fetch_dreams_dataframe
from modules.visuals import correlation_scatter, emotion_distribution_pie

st.title("🧭 Insights")

df = fetch_dreams_dataframe()
if df.empty:
    st.info("Log a dream to see insights.")
    st.stop()

st.subheader("Emotion distribution")
st.plotly_chart(emotion_distribution_pie(df), use_container_width=True)

st.subheader("Sleep vs. Negative Affect")
# Define negative affect as (fear+sadness+anger+disgust)
neg = df.apply(lambda r: r["emotions"].get("fear",0)+r["emotions"].get("sadness",0)+r["emotions"].get("anger",0)+r["emotions"].get("disgust",0), axis=1)
df["neg_affect"] = neg

col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(correlation_scatter(df, x="sleep_hours", y="neg_affect", title="Sleep Hours vs Negative Affect"), use_container_width=True)
with col2:
    st.plotly_chart(correlation_scatter(df, x="sleep_quality", y="neg_affect", title="Sleep Quality vs Negative Affect"), use_container_width=True)

# Simple feedback text
st.subheader("Personalized feedback")
last_n = st.slider("Analyze last N dreams", 3, min(30, len(df)), min(10, len(df)))
recent = df.tail(last_n)
avg_neg = recent["neg_affect"].mean() if not recent.empty else 0
if avg_neg >= 50:
    st.warning("You've had a run of **fear/sadness/anger** leaning dreams recently. If possible, try winding down earlier, reduce late screens, or consider a brief pre-sleep journaling session.")
elif avg_neg >= 25:
    st.info("Mixed emotional tone lately. Light relaxation before bed and consistent sleep times might help tilt dreams positively.")
else:
    st.success("Your recent dreams skew calmer/neutral. Keep steady routines and hydration; you're on a good trend!")
