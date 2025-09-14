# pages/2_📊_History.py
from __future__ import annotations

import streamlit as st
import pandas as pd

# Auth (require login + user info)
from modules.auth import require_login, current_user, user_greeting, logout_button

# Storage (per-user)
from modules.storage import fetch_dreams_dataframe  # now requires user_email

# Visuals
from modules.visuals import emotion_arc_chart, wordcloud_image, emotion_node_graph

from modules.auth import require_login, current_user, user_greeting, logout_button
require_login("Please sign up or sign in to view this page.")

from components.ui import render_top_nav
render_top_nav(hide_sidebar=True)



# -------------------------- Page --------------------------

require_login()
user = current_user()
if not user:
    st.stop()  # {'email': ..., 'name': ...}

st.title("📊 History")
#user_greeting()
#logout_button()

# Pull only THIS user's dreams
df = fetch_dreams_dataframe(user["email"])
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
        # df contains columns: created_at, emotions (dict), top_emotion, etc.
        st.plotly_chart(emotion_arc_chart(df), use_container_width=True)
    with colB:
        # wordcloud_image expects a series/list-like of motif lists
        img = wordcloud_image(df["motifs"])
        st.image(img, caption="Motif cloud", use_column_width=True)

# --- State for which card is open ---
if "view_id" not in st.session_state:
    st.session_state.view_id = None

# --- Card list with per-dream VIEW ---
for _, row in df.sort_values("created_at", ascending=False).iterrows():
    created = pd.to_datetime(row["created_at"]).strftime("%B %d, %Y %I:%M %p")
    pos_em = (row.get("top_emotion") or "neutral").capitalize()
    arche = (row.get("archetype") or "Unknown").capitalize()

    st.markdown(f"""
    <div class="card">
      <div style="display:flex;justify-content:space-between;align-items:center;">
        <div>
          <div style="font-weight:800;font-size:18px;">{created}</div>
          <div style="opacity:.85;margin-top:2px;">{row.get("preview","")}</div>
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
        # Optional: hook up a delete endpoint later (per-user)
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
                st.write(row.get("text",""))
                st.write("**Tags:**", row.get("tags") or "—")
                st.write("**Sleep:**", f"{row.get('sleep_hours','—')}h · quality {row.get('sleep_quality','—')}/5")
            with tabs[1]:
                # row["emotions"] is already a dict from storage.decode()
                st.plotly_chart(emotion_node_graph(row.get("emotions", {})), use_container_width=True)
            with tabs[2]:
                st.write("**Top Archetype:**", arche if arche else "—")
            with tabs[3]:
                st.write(row.get("reframed") or "—")
            st.markdown('</div>', unsafe_allow_html=True)
