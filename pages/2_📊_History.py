import streamlit as st
import pandas as pd
import numpy as np
from modules.storage import fetch_dreams_dataframe
from modules.visuals import emotion_arc_chart, wordcloud_image, emotion_node_graph

st.title("📊 History")

df = fetch_dreams_dataframe()
if df.empty:
    st.info("No dreams yet. Log one from the **Analyze** page.")
    st.stop()

# --- Styles for cards/buttons ---
st.markdown("""
<style>
.card {
  background: rgba(255,255,255,.04);
  border: 1px solid rgba(255,255,255,.12);
  border-radius: 16px; padding: 16px 18px; margin-bottom: 14px;
}
.badge {
  display:inline-block; padding: 4px 10px; border-radius: 999px;
  font-size:12px; font-weight:700; margin-right:6px; background: rgba(255,255,255,.12);
}
.btn {
  padding: 6px 10px; border-radius: 10px; font-weight:700; border:1px solid rgba(255,255,255,.2);
  background: rgba(255,255,255,.06); color: #eaeaff; text-decoration: none; margin-left: 6px;
}
.detail {
  background: rgba(0,0,0,.35);
  border: 1px dashed rgba(255,255,255,.2);
  border-radius: 14px; padding: 14px; margin-top: 10px;
}
</style>
""", unsafe_allow_html=True)

# --- Summary visuals ---
with st.expander("Overview charts", expanded=True):
    colA, colB = st.columns([2,1])
    with colA:
        st.plotly_chart(emotion_arc_chart(df), use_container_width=True)
    with colB:
        img = wordcloud_image(df["motifs"])
        st.image(img, caption="Motif cloud", use_column_width=True)

# --- Card list with per-dream VIEW ---
if "view_id" not in st.session_state:
    st.session_state.view_id = None

for i, row in df.sort_values("created_at", ascending=False).iterrows():
    created = pd.to_datetime(row["created_at"]).strftime("%B %d, %Y %I:%M %p")
    pos_em = row["top_emotion"].capitalize()
    arche = row["archetype"].capitalize() if row["archetype"] else "Unknown"

    st.markdown(f"""
    <div class="card">
      <div style="display:flex;justify-content:space-between;align-items:center;">
        <div>
          <div style="font-weight:800;font-size:18px;">{created}</div>
          <div style="opacity:.85;margin-top:2px;">{row["preview"]}</div>
          <div style="margin-top:8px;">
            <span class="badge">{arche}</span>
            <span class="badge">{pos_em}</span>
          </div>
        </div>
        <div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("👁 View", key=f"view_{row['id']}"):
            st.session_state.view_id = row["id"]
    with col2:
        if st.button("🗑 Delete", key=f"del_{row['id']}"):
            st.warning("Delete not implemented in this view. (Ask if you want me to add it.)")

    st.markdown("</div></div>", unsafe_allow_html=True)

    # --- Detail view for this card ---
    if st.session_state.view_id == row["id"]:
        with st.container():
            st.markdown('<div class="detail">', unsafe_allow_html=True)
            tabs = st.tabs(["Overview","Emotions","Archetype","Reframe"])
            with tabs[0]:
                st.write("**Dream Text**")
                st.write(row["text"])
                st.write("**Tags:**", row["tags"] or "—")
                st.write("**Sleep:**", f"{row['sleep_hours']}h · quality {row['sleep_quality']}/5")
            with tabs[1]:
                st.plotly_chart(emotion_node_graph(row["emotions"]), use_container_width=True)
            with tabs[2]:
                st.write("**Top Archetype:**", row["archetype"].capitalize() if row["archetype"] else "—")
            with tabs[3]:
                st.write(row["reframed"] or "—")
            st.markdown('</div>', unsafe_allow_html=True)
