# pages/4_⚙️_Settings.py
from __future__ import annotations

import streamlit as st
import pandas as pd

# Auth
from modules.auth import require_login, current_user, user_greeting, logout_button

# Storage (per-user)
from modules.storage import fetch_dreams_dataframe, wipe_user_data

from modules.auth import require_login, current_user, user_greeting, logout_button
require_login("Please sign up or sign in to view this page.")
from components.ui import render_top_nav
render_top_nav(hide_sidebar=True)


# ---------- Page ----------

require_login()
user = current_user()
if not user:
    st.stop()

st.title("⚙️ Settings")
#user_greeting()
#logout_button()

st.subheader("Account info")
st.write("**Name:**", user["name"])
st.write("**Email:**", user["email"])

st.divider()

# --- Data management ---
st.subheader("My data")

col1, col2 = st.columns(2)
with col1:
    if st.button("⬇️ Export my dreams as CSV"):
        df = fetch_dreams_dataframe(user["email"])
        if df.empty:
            st.info("No dreams to export.")
        else:
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Download CSV",
                data=csv,
                file_name=f"noctimind_dreams_{user['email'].replace('@','_at_')}.csv",
                mime="text/csv"
            )

with col2:
    if st.button("🗑 Clear all my dreams"):
        wipe_user_data(user["email"])
        st.success("All your dreams were deleted.")
        st.rerun()

st.divider()
st.caption("More settings coming soon (notifications, themes, export to PDF, etc.)")
