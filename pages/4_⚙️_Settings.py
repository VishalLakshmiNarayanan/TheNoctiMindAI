import streamlit as st
from modules.storage import wipe_all_data

st.title("⚙️ Settings")
st.caption("You can override defaults below.")

with st.expander("API / Model"):
    st.write("Set `GROQ_API_KEY` and `GROQ_MODEL` in `.streamlit/secrets.toml` or `.env`.")

with st.expander("Danger zone"):
    if st.button("Delete all data (irreversible)"):
        wipe_all_data()
        st.success("All data removed. Refresh the app.")
