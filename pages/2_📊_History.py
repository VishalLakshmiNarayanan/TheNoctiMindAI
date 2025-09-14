# pages/2_📊_History.py
from __future__ import annotations

import streamlit as st
import pandas as pd

# Timezone (client)
try:
    from streamlit_js_eval import get_user_timezone
    USER_TZ = get_user_timezone() or "UTC"
except Exception:
    USER_TZ = "UTC"

# Auth
from modules.auth import require_login, current_user

# Storage (per-user)
from modules.storage import fetch_dreams_dataframe

# Visuals
from modules.visuals import emotion_arc_chart, wordcloud_image, emotion_node_graph

# shadcn helpers
from components.shad_theme import use_page, header, nav_tabs, card



# -------------------------- Page shell --------------------------
use_page("History · NoctiMind", hide_sidebar=True)
require_login("Please sign up or sign in to view this page.")
user = current_user()
if not user:
    st.stop()

header()
nav_tabs("Dream History")

# (Optional routing)
# if active == "Overview": st.switch_page("app.py")
# if active == "Reports": st.switch_page("pages/3_🧭_Insights.py")
# if active == "Notifications": st.switch_page("pages/1_📘_Log_a_Dream.py")


# -------------------------- Data --------------------------
df = fetch_dreams_dataframe(user["email"])
if df.empty:
    st.info("No dreams yet. Log one from the **Analyze** page.")
    st.stop()

# ⏰ Localize created_at to the user's timezone
import pytz
from datetime import datetime

try:
    from streamlit_js_eval import get_user_timezone
    tzname = get_user_timezone()
except Exception:
    tzname = None

if not tzname:
    tzname = "UTC"  # fallback

USER_TZ = pytz.timezone(tzname)

df["created_at"] = (
    pd.to_datetime(df["created_at"], utc=True, errors="coerce")
      .dt.tz_convert(USER_TZ)
)



# -------------------------- Overview Charts (card) --------------------------
def _overview_charts():
    colA, colB = st.columns([2, 1])
    with colA:
        st.plotly_chart(emotion_arc_chart(df), use_container_width=True)

    with colB:
        texts = df["text"].fillna("").tolist() if "text" in df else []
        img = wordcloud_image(texts)
        # ✅ fix deprecation
        st.image(img, caption="Motif/keyword cloud", use_container_width=True)

card("Overview", _overview_charts)


# -------------------------- Dream list (card) --------------------------
def _history_list():
    # Render each dream newest->oldest
    for _, row in df.sort_values("created_at", ascending=False).iterrows():
        # already tz-aware; format in a friendly way
        created = pd.to_datetime(row["created_at"]).strftime("%b %d, %Y %I:%M %p")
        arche = (row.get("archetype") or "Unknown").capitalize()
        pos_em = (row.get("top_emotion") or "neutral").capitalize()

        # A neat expander per dream acts like your “View” button + detail
        preview = (row.get("preview") or row.get("text") or "")
        preview = (preview[:140] + "…") if isinstance(preview, str) and len(preview) > 140 else preview

        with st.expander(f"{created} — {arche} • {pos_em}"):
            # Top row: quick facts
            c1, c2, c3 = st.columns([0.55, 0.22, 0.23])
            with c1:
                st.caption("Preview")
                st.write(preview or "—")
            with c2:
                st.caption("Archetype")
                st.write(arche or "—")
            with c3:
                st.caption("Top Emotion")
                st.write(pos_em or "—")

            st.divider()

            tabs = st.tabs(["Overview", "Emotions", "Archetype", "Reframe"])
            with tabs[0]:
                st.write("**Dream Text**")
                st.write(row.get("text", ""))
                st.write("**Tags:**", row.get("tags") or "—")
                st.write(
                    "**Sleep:**",
                    f"{row.get('sleep_hours','—')}h · quality {row.get('sleep_quality','—')}/5",
                )

            with tabs[1]:
                st.plotly_chart(
                    emotion_node_graph(row.get("emotions", {})),
                    use_container_width=True
                )

            with tabs[2]:
                st.write("**Top Archetype:**", arche if arche else "—")

            with tabs[3]:
                st.write(row.get("reframed") or "—")

card("Dream History", _history_list)
