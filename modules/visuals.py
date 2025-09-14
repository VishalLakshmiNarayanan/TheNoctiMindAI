# modules/visuals.py
from __future__ import annotations
import math
from typing import Dict, Iterable, List, Tuple, Any

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud, STOPWORDS

# ------------------------------------------------------------
# Emotion configuration
# ------------------------------------------------------------
EMOTION_ORDER = ["joy","sadness","fear","anger","disgust","surprise","neutral"]
EMOTION_PALETTE = {
    "joy":      "#F9D423",  # warm yellow
    "sadness":  "#4A90E2",  # blue
    "fear":     "#9B59B6",  # purple
    "anger":    "#E74C3C",  # red
    "disgust":  "#2ECC71",  # green
    "surprise": "#F5A623",  # orange
    "neutral":  "#95A5A6",  # gray
}

def _ordered_items(emotions: Dict[str, float]) -> List[Tuple[str, float]]:
    """Return (emotion, value) following EMOTION_ORDER and filling missing as 0."""
    emotions = emotions or {}
    return [(k, float(emotions.get(k, 0.0))) for k in EMOTION_ORDER]

# ------------------------------------------------------------
# Emotion breakdown (Bar) – colored by emotion
# ------------------------------------------------------------
def render_emotion_bar(emotions: Dict[str, float]):
    import streamlit as st
    data = _ordered_items(emotions)
    df = pd.DataFrame({
        "emotion": [k.capitalize() for k, _ in data],
        "value": [v for _, v in data],
        "key": [k for k, _ in data],
    })
    colors = [EMOTION_PALETTE[k] for k in df["key"]]
    fig = go.Figure(
        data=[go.Bar(
            x=df["emotion"],
            y=df["value"],
            marker=dict(color=colors),
            hovertemplate="%{x}: %{y:.1f}%<extra></extra>",
        )]
    )
    fig.update_layout(
        title="Emotion breakdown (%)",
        height=300,
        margin=dict(l=10, r=10, t=40, b=10),
        xaxis_title="",
        yaxis_title="%",
        template="plotly_dark",
    )
    st.plotly_chart(fig, use_container_width=True)

# ------------------------------------------------------------
# Emotion arcs over time – colored by emotion
# ------------------------------------------------------------
def emotion_arc_chart(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return go.Figure()
    rows = []
    for _, r in df.iterrows():
        row = {"created_at": r["created_at"]}
        emo = r.get("emotions") or {}
        for k in EMOTION_ORDER:
            row[k] = float(emo.get(k, 0.0))
        rows.append(row)
    wide = pd.DataFrame(rows)
    wide["created_at"] = pd.to_datetime(wide["created_at"])
    long = wide.melt(id_vars="created_at", var_name="emotion", value_name="percent")

    color_map = {k: EMOTION_PALETTE[k] for k in EMOTION_ORDER}
    fig = px.line(
        long, x="created_at", y="percent", color="emotion",
        color_discrete_map=color_map, title="Emotion arcs over time"
    )
    fig.update_traces(mode="lines+markers", hovertemplate="%{legendgroup}: %{y:.1f}%<extra></extra>")
    fig.update_layout(
        height=360, template="plotly_dark",
        margin=dict(l=10, r=10, t=40, b=10),
        xaxis_title="Time", yaxis_title="%",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0.0)
    )
    return fig

# ------------------------------------------------------------
# WordCloud from motifs
# ------------------------------------------------------------


def wordcloud_image(texts) -> "PIL.Image.Image":
    """
    Build a word cloud from a list of strings.
    - Adds domain stopwords to avoid 'dream' dominating.
    - Returns a PIL image you can st.image(..., use_container_width=True).
    """
    # Normalize input -> one big string
    if isinstance(texts, (list, tuple)):
        corpus = " ".join([str(t or "") for t in texts])
    elif isinstance(texts, str):
        corpus = texts
    else:
        corpus = ""

    # Enrich stopwords – tune as needed
    extra_stops = {
        "dream", "dreams", "like", "really", "just", "one", "get", "got",
        "see", "saw", "go", "went", "feel", "felt", "know", "think",
        "wake", "woke", "woken", "night", "day", "time"
    }
    stops = STOPWORDS.union(extra_stops)

    wc = WordCloud(
        width=1000,
        height=500,
        background_color="white",
        stopwords=stops,
        collocations=False,   # prevents bigrams like "dream dream"
        prefer_horizontal=0.95,
    )
    return wc.generate(corpus).to_image()


# ------------------------------------------------------------
# Correlation scatter with trendline
# ------------------------------------------------------------
def correlation_scatter(df: pd.DataFrame, x: str, y: str, title: str = "Correlation"):
    import plotly.express as px
    import plotly.graph_objects as go

    # Base scatter
    fig = px.scatter(df, x=x, y=y, title=title)

    # Lightweight OLS via NumPy (no statsmodels dependency)
    try:
        xs = pd.to_numeric(df[x], errors="coerce").to_numpy()
        ys = pd.to_numeric(df[y], errors="coerce").to_numpy()
        mask = np.isfinite(xs) & np.isfinite(ys)
        xs = xs[mask]
        ys = ys[mask]

        if xs.size >= 2:
            # slope, intercept for y = m*x + b
            slope, intercept = np.polyfit(xs, ys, 1)
            xline = np.linspace(xs.min(), xs.max(), 100)
            yline = slope * xline + intercept

            fig.add_trace(
                go.Scatter(
                    x=xline,
                    y=yline,
                    mode="lines",
                    name="Trendline",
                    hovertemplate="Trend: %{y:.3f}<extra></extra>"
                )
            )

            # R^2 for context
            yhat = slope * xs + intercept
            ss_res = np.sum((ys - yhat) ** 2)
            ss_tot = np.sum((ys - ys.mean()) ** 2)
            r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0
            fig.update_layout(title=f"{title} (R²={r2:.3f})")
    except Exception:
        # If anything goes wrong, just show the scatter without a line
        pass

    fig.update_traces(hovertemplate=f"{x}: "+"%{x}<br>"+f"{y}: "+"%{y}<extra></extra>")
    return fig

# ------------------------------------------------------------
# Emotion distribution (Pie) – colored by emotion
# ------------------------------------------------------------
def emotion_distribution_pie(data) -> "go.Figure":
    """
    Build a pie chart for emotion distribution.

    Accepts:
      - dict: {"joy": %, "sadness": %, ...}
      - DataFrame: with 'emotions' column (dict per row), or per-emotion columns
      - list[dict]: list of emotion dicts

    Returns:
      plotly.graph_objects.Figure
    """
    import plotly.express as px

    keys = EMOTION_ORDER

    # ---- Normalize input into a list of dicts ----
    items = []

    if isinstance(data, dict):
        items = [data]

    elif isinstance(data, pd.DataFrame):
        if "emotions" in data.columns:
            items = [e for e in data["emotions"].dropna().tolist() if isinstance(e, dict)]
        else:
            # Fall back: try to read columns directly if present
            for _, row in data.iterrows():
                d = {k: float(row.get(k, 0.0)) if k in row else 0.0 for k in keys}
                items.append(d)

    elif isinstance(data, (list, tuple)):
        items = [e for e in data if isinstance(e, dict)]

    # ---- Compute average distribution ----
    sums = {k: 0.0 for k in keys}
    n = 0
    for em in items:
        for k in keys:
            try:
                sums[k] += float(em.get(k, 0.0))
            except Exception:
                pass
        n += 1

    if n == 0:
        avg = {k: (100.0 if k == "neutral" else 0.0) for k in keys}
    else:
        avg = {k: round(sums[k] / n, 4) for k in keys}

    # Optional: re-normalize to sum ~100 if desired
    total = sum(avg.values())
    if total > 0:
        avg = {k: (v / total) * 100.0 for k, v in avg.items()}

    # ---- Build pie ----
    df_plot = pd.DataFrame({"emotion": [k.capitalize() for k in keys],
                            "key": keys,
                            "value": [avg[k] for k in keys]})
    color_map = {k: EMOTION_PALETTE[k] for k in keys}

    fig = px.pie(
        df_plot,
        names="emotion",
        values="value",
        color="key",
        color_discrete_map=color_map,
        hole=0.35,
        title="Emotion distribution"
    )
    fig.update_traces(hovertemplate="%{label}: %{value:.1f}%<extra></extra>")
    return fig

# ------------------------------------------------------------
# Emotion Map (circular) – top emotion blinks
# ------------------------------------------------------------
def emotion_node_graph(emotions: Dict[str, float], blink_top: bool = True) -> go.Figure:
    """
    Circular node map:
      - Color = palette per emotion
      - Size = percentage
      - Top emotion blinks (opacity + outline width)
      - ▶ button moved to top-left, with label showing which emotion is highlighted
    """
    items = _ordered_items(emotions)
    keys = [k for k, _ in items]
    labels = [k.capitalize() for k in keys]
    vals = np.array([v for _, v in items], dtype=float)

    n = len(items)
    if n == 0:
        return go.Figure()

    # Circle layout
    R = 1.0
    angles = np.linspace(0, 2*math.pi, n, endpoint=False)
    xs = R * np.cos(angles)
    ys = R * np.sin(angles)

    sizes = 12 + 0.6 * vals   # visual size
    colors = [EMOTION_PALETTE[k] for k in keys]
    top_idx = int(np.argmax(vals)) if len(vals) else 0
    top_label = labels[top_idx]

    # Base traces
    circle_trace = go.Scatter(
        x=list(xs)+[xs[0]], y=list(ys)+[ys[0]],
        mode="lines",
        line=dict(color="rgba(255,255,255,0.15)", width=1, dash="dot"),
        hoverinfo="skip", showlegend=False,
    )
    base_nodes = go.Scatter(
        x=xs, y=ys, mode="markers+text",
        text=[f"{labels[i]}<br>{vals[i]:.0f}%" for i in range(n)],
        textposition="top center",
        marker=dict(
            size=sizes,
            color=colors,
            line=dict(color="white", width=[3 if i == top_idx else 1 for i in range(n)]),
            opacity=1.0
        ),
        hovertemplate="%{text}<extra></extra>",
        showlegend=False,
    )

    fig = go.Figure(data=[circle_trace, base_nodes])
    fig.update_layout(
        title="Emotion Map",
        height=420,
        margin=dict(l=10, r=10, t=50, b=10),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False, scaleanchor="x", scaleratio=1),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        template="plotly_dark",
    )

    if not blink_top:
        # Put the label even if we don't animate
        fig.add_annotation(
            xref="paper", yref="paper", x=0.12, y=0.98,
            xanchor="left", yanchor="top",
            text=f"Highlighting: <b>{top_label}</b>",
            showarrow=False,
            font=dict(size=12, color="#eaeaea"),
        )
        return fig

    # Animation frames for blinking the top emotion
    def frame(marker_opacity: float, line_width_on: float) -> go.Frame:
        lw = [line_width_on if i == top_idx else 1 for i in range(n)]
        opac = [marker_opacity if i == top_idx else 1.0 for i in range(n)]
        return go.Frame(
            data=[
                circle_trace,
                go.Scatter(
                    x=xs, y=ys, mode="markers+text",
                    text=[f"{labels[i]}<br>{vals[i]:.0f}%" for i in range(n)],
                    textposition="top center",
                    marker=dict(size=sizes, color=colors, line=dict(color="white", width=lw), opacity=opac),
                    hovertemplate="%{text}<extra></extra>",
                    showlegend=False,
                )
            ]
        )

    fig.frames = [
        frame(marker_opacity=1.0, line_width_on=6),   # ON (bold + opaque)
        frame(marker_opacity=0.2, line_width_on=1),   # OFF (dim + thin)
    ]

    # Move the ▶ button away from the plot and add a label next to it
    fig.update_layout(
        updatemenus=[dict(
            type="buttons",
            showactive=False,
            buttons=[dict(
                label="▶",
                method="animate",
                args=[None, dict(
                    frame=dict(duration=500, redraw=True),
                    transition=dict(duration=0),
                    fromcurrent=True,
                    mode="immediate"
                )],
            )],
            x=0.02, y=0.98,             # <-- top-left of the full figure ("paper" coords)
            xanchor="left", yanchor="top",
            pad=dict(r=4, t=4, b=4, l=4),
            bgcolor="rgba(30,30,40,0.6)",
            bordercolor="rgba(255,255,255,0.2)",
            borderwidth=1,
        )],
        sliders=[],
    )

    # Text beside the button
    fig.add_annotation(
        xref="paper", yref="paper", x=0.12, y=0.98,
        xanchor="left", yanchor="top",
        text=f"Highlighting: <b>{top_label}</b>",
        showarrow=False,
        font=dict(size=12, color="#eaeaea"),
        align="left",
        bgcolor="rgba(0,0,0,0)",
    )

    return fig
