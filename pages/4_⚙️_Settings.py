# pages/4_⚙️_Settings.py
from __future__ import annotations

import streamlit as st
import pandas as pd

# Auth
from modules.auth import require_login, current_user

# Storage (per-user)
from modules.storage import fetch_dreams_dataframe, wipe_user_data

# shadcn helpers
from components.shad_theme import use_page, header, nav_tabs, card


# -------------------------- Page shell --------------------------
use_page("Settings · NoctiMind", hide_sidebar=True)
require_login("Please sign up or sign in to view this page.")
user = current_user()
if not user:
    st.stop()

header()
nav_tabs("Settings")

 # choose any default; Settings isn't in the 4 tabs but we keep the look
# (Optional) add routing if you want:
# if active == "Analytics": st.switch_page("pages/2_📊_History.py")
# if active == "Reports": st.switch_page("pages/3_🧭_Insights.py")
# if active == "Notifications": st.switch_page("pages/1_📘_Log_a_Dream.py")

# -------------------------- Data --------------------------
df = fetch_dreams_dataframe(user["email"])

# -------------------------- Account Info (card) --------------------------
def _account_info():
    st.write("**Name:**", user["name"])
    st.write("**Email:**", user["email"])

card("Account Info", _account_info)

# -------------------------- My Data (card) --------------------------
def _my_data():
    c1, c2 = st.columns(2)

    # Export CSV
    with c1:
        st.subheader("Export")
        if df.empty:
            st.info("No dreams to export.")
        else:
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="⬇️ Download my dreams (CSV)",
                data=csv,
                file_name=f"noctimind_dreams_{user['email'].replace('@','_at_')}.csv",
                mime="text/csv",
                use_container_width=True,
            )

    # Clear data (with confirm)
    with c2:
        st.subheader("Delete")
        confirm = st.checkbox("I understand this will permanently delete all my dreams.", value=False)
        if st.button("🗑 Clear all my dreams", type="primary", use_container_width=True, disabled=not confirm):
            wipe_user_data(user["email"])
            st.success("All your dreams were deleted.")
            st.rerun()

card("My Data", _my_data)

st.caption("More settings coming soon (notifications, themes, export to PDF, etc.)")
