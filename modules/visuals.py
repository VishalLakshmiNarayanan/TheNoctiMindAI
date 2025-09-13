import io
import numpy as np
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud
from PIL import Image

def render_emotion_bar(emotions: dict):
    import streamlit as st
    df = pd.DataFrame({"emotion": list(emotions.keys()), "value": list(emotions.values())})
    fig = px.bar(df, x="emotion", y="value", title="Emotion breakdown (%)", labels={"value":"%"} )
    st.plotly_chart(fig, use_container_width=True)

def emotion_arc_chart(df: pd.DataFrame):
    # expand each emotion into columns for plotting over time index
    emo_keys = ["joy","sadness","fear","anger","disgust","surprise","neutral"]
    rows = []
    for _, r in df.iterrows():
        row = {"created_at": r["created_at"]}
        for k in emo_keys:
            row[k] = r["emotions"].get(k,0)
        rows.append(row)
    wide = pd.DataFrame(rows)
    wide["created_at"] = pd.to_datetime(wide["created_at"])
    long = wide.melt(id_vars="created_at", var_name="emotion", value_name="percent")
    fig = px.line(long, x="created_at", y="percent", color="emotion", title="Emotion arcs over time")
    fig.update_traces(mode="lines+markers")
    return fig

def wordcloud_image(motifs_series: pd.Series):
    text = " ".join([m for row in motifs_series if isinstance(row, list) for m in row])
    if not text.strip():
        text = "dream"
    wc = WordCloud(width=1000, height=400, background_color="white").generate(text)
    img = wc.to_image()
    return img

def correlation_scatter(df: pd.DataFrame, x: str, y: str, title: str):
    fig = px.scatter(df, x=x, y=y, trendline="ols", title=title)
    return fig

def emotion_distribution_pie(df: pd.DataFrame):
    # average emotion percentages across dreams
    keys = ["joy","sadness","fear","anger","disgust","surprise","neutral"]
    acc = {k:0.0 for k in keys}
    n = max(len(df), 1)
    for _, r in df.iterrows():
        for k in keys:
            acc[k] += r["emotions"].get(k,0.0)
    acc = {k: v / n for k,v in acc.items()}
    p = pd.DataFrame({"emotion": list(acc.keys()), "value": list(acc.values())})
    fig = px.pie(p, names="emotion", values="value", title="Avg emotion mix")
    return fig
