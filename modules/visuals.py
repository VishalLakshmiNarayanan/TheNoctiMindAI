import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx
from wordcloud import WordCloud

# ---------- Existing helper charts ----------
def render_emotion_bar(emotions: dict):
    import streamlit as st
    df = pd.DataFrame({"emotion": list(emotions.keys()), "value": list(emotions.values())})
    fig = px.bar(df, x="emotion", y="value", title="Emotion breakdown (%)", labels={"value":"%"} )
    st.plotly_chart(fig, use_container_width=True)

def emotion_arc_chart(df: pd.DataFrame):
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

# ---------- NEW: Emotion Map (node graph) ----------
_DEFAULT_EDGES = [
    ("joy","surprise"),
    ("joy","neutral"),
    ("sadness","fear"),
    ("sadness","anger"),
    ("fear","surprise"),
    ("anger","disgust"),
    ("disgust","fear"),
    ("neutral","joy"),
    ("neutral","sadness"),
]
_EMO_KEYS = ["joy","sadness","fear","anger","disgust","surprise","neutral"]

def emotion_node_graph(emotions: dict):
    """
    Build a simple network of core emotions. Node size = intensity, opacity = intensity.
    Lights up nodes with nonzero intensity; others are dimmed.
    """
    # sanitize
    vals = {k: float(max(0.0, emotions.get(k, 0.0))) for k in _EMO_KEYS}
    total = sum(vals.values()) or 1.0
    # Normalize to 0..100 for display, preserve 0s
    vals = {k: 100.0 * v / total if total else 0.0 for k, v in vals.items()}

    G = nx.Graph()
    for k in _EMO_KEYS:
        G.add_node(k, weight=vals[k])
    G.add_edges_from(_DEFAULT_EDGES)

    # layout
    pos = nx.spring_layout(G, seed=7, k=0.9)

    # node styling
    xs, ys, sizes, texts, opacities = [], [], [], [], []
    for n, p in pos.items():
        xs.append(p[0]); ys.append(p[1])
        size = 20 + (vals[n] * 0.8)  # 20..100-ish
        sizes.append(size)
        texts.append(f"{n}: {vals[n]:.1f}%")
        opacities.append(0.25 if vals[n] < 1e-3 else 0.95)

    node_trace = go.Scatter(
        x=xs, y=ys, mode='markers+text',
        text=[k.capitalize() for k in _EMO_KEYS],
        textposition="top center",
        marker=dict(
            size=sizes,
            color=vals_to_color([vals[k] for k in _EMO_KEYS]),
            opacity=opacities,
            line=dict(width=2, color="rgba(255,255,255,0.75)")
        ),
        hovertext=texts,
        hoverinfo="text"
    )

    # edges as line segments
    ex, ey = [], []
    for u, v in _DEFAULT_EDGES:
        ex += [pos[u][0], pos[v][0], None]
        ey += [pos[u][1], pos[v][1], None]
    edge_trace = go.Scatter(x=ex, y=ey, mode='lines', line=dict(width=1, color='rgba(200,200,220,0.35)'), hoverinfo='none')

    fig = go.Figure(data=[edge_trace, node_trace])
    fig.update_layout(
        title="Emotion Map",
        showlegend=False,
        xaxis=dict(visible=False), yaxis=dict(visible=False),
        margin=dict(l=10,r=10,t=40,b=10),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)"
    )
    return fig

def vals_to_color(values):
    """Map 0..100 to a purple→pink ramp (no explicit color names; numeric RGBA)."""
    colors = []
    for v in values:
        # 0 → 120; 100 → 255
        c = int(120 + (v/100.0) * 135)
        colors.append(f"rgba({c-60},{c-40},{255},0.95)")
    return colors
