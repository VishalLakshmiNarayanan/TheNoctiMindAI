import streamlit as st
import pandas as pd
import numpy as np
from modules.storage import fetch_dreams_dataframe
from modules.visuals import emotion_arc_chart, wordcloud_image
from modules.nlp import cosine_sim_matrix, group_by_top_emotion, dominant_emotion
from sklearn.cluster import KMeans

st.title("📊 History & Similarity")

df = fetch_dreams_dataframe()
if df.empty:
    st.info("No dreams yet. Log one from the **Log a Dream** page.")
    st.stop()

# Basic table
st.subheader("Your Dream Log")
st.dataframe(df[["created_at","archetype","top_emotion","sleep_hours","sleep_quality","motifs","preview"]].sort_values("created_at", ascending=False), use_container_width=True)

# Emotion arcs over time
st.subheader("Emotion arcs over time")
st.plotly_chart(emotion_arc_chart(df), use_container_width=True)

# Word cloud of motifs
st.subheader("Motif cloud")
img = wordcloud_image(df["motifs"])
st.image(img, caption="Frequent motifs")

# Similarity grouping
st.subheader("Similarity groups")
embs = np.vstack(df["embedding"].to_list())
k = st.slider("Number of similarity clusters (k)", 2, min(10, len(df)), 4)
km = KMeans(n_clusters=k, n_init="auto", random_state=42)
labels = km.fit_predict(embs)
df["cluster"] = labels

# Show grouped by cluster with representative emotion/archetype
for c in sorted(df["cluster"].unique()):
    sub = df[df["cluster"] == c]
    st.markdown(f"### Group {c} · {len(sub)} dreams")
    # summarize
    rep_em = sub["top_emotion"].mode().iat[0] if not sub.empty else "—"
    rep_arch = sub["archetype"].mode().iat[0] if not sub.empty else "—"
    st.caption(f"Dominant emotion: **{rep_em}** · Dominant archetype: **{rep_arch}**")
    st.dataframe(sub[["created_at","top_emotion","archetype","preview"]].sort_values("created_at", ascending=False), use_container_width=True)

# Grouping tab: by emotion / archetype
st.subheader("Group by Emotion / Archetype")
tab1, tab2 = st.tabs(["By Emotion", "By Archetype"])
with tab1:
    for em in sorted(df["top_emotion"].unique()):
        sub = df[df["top_emotion"] == em].sort_values("created_at", ascending=False)
        st.markdown(f"#### {em} · {len(sub)}")
        st.dataframe(sub[["created_at","archetype","preview"]], use_container_width=True)

with tab2:
    for arch in sorted(df["archetype"].unique()):
        sub = df[df["archetype"] == arch].sort_values("created_at", ascending=False)
        st.markdown(f"#### {arch} · {len(sub)}")
        st.dataframe(sub[["created_at","top_emotion","preview"]], use_container_width=True)
