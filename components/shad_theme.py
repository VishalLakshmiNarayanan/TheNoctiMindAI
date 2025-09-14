from __future__ import annotations
import re
import streamlit as st

try:
    import streamlit_shadcn_ui as ui
except Exception:
    ui = None


def use_page(title: str = "NoctiMind", description: str = "Dreams · Insights · Wellness", hide_sidebar: bool = True):
    st.set_page_config(page_title=title, page_icon="🌙", layout="wide")
    # remember a page id for unique keys
    st.session_state["_shad_page_id"] = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-") or "root"
    _inject_css(hide_sidebar)

def _inject_css(hide_sidebar: bool):
    st.markdown(
        f"""
        <style>
          /* Optional: hide sidebar + hamburger */
          {"[data-testid='stSidebar'],[data-testid='stSidebarNav']{{display:none !important;}}"
            "[data-testid='stToolbar'] button[kind='header']{{display:none !important;}}"
            ".main .block-container{{padding-top:0.75rem; max-width:1200px;}}" if hide_sidebar else ""}

          /* shadcn-like header */
          .nm-header {{
            background: rgba(255,255,255,.02);
            border: 1px solid rgba(255,255,255,.08);
            border-radius: 16px;
            padding: 18px 16px;
            margin-bottom: 12px;
          }}
          .nm-title {{ font-weight: 800; font-size: 1.25rem; margin: 2px 0; }}
          .nm-sub   {{ opacity: .75; font-size: 0.95rem; }}

          /* Tabs spacing */
          .stTabs [data-baseweb="tab-list"] {{ gap: 6px; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# ---------- Header (no buttons) ----------
def header(title: str = "Streamlit Shadcn UI",
           subtitle: str = "A Streamlit component library for building beautiful apps easily. "
                           "Bring the power of shadcn/ui to your Streamlit apps!"):
    st.markdown('<div class="nm-header">', unsafe_allow_html=True)
    st.markdown(f'<div class="nm-title">{title}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="nm-sub">{subtitle}</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ---------- Tabs that actually navigate ----------
_ROUTE_MAP = {
    "Home":       "app.py",
    "Dream History":      "pages/2_📊_History.py",
    "Dream Insights":        "pages/3_🧭_Insights.py",
    "Dream Logs":  "pages/1_📘_Log_a_Dream.py",
    "Settings":       "pages/4_⚙️_Settings.py",
}

def nav_tabs(current: str = "Overview", key: str | None = None):
    """
    Render tabs and navigate with st.switch_page when changed.
    Uses a per-page unique key to avoid duplicate-key errors.
    """
    options = list(_ROUND_TRIP_ORDER())
    default = current if current in options else options[0]

    # unique key per page (e.g., nm_tabs_nav-overview, nm_tabs_nav-history, ...)
    page_id = st.session_state.get("_shad_page_id", "root")
    comp_key = key or f"nm_tabs_nav-{page_id}"

    if ui:
        selected = ui.tabs(options=options, default_value=default, key=comp_key)
    else:
        # fallback: non-interactive; keep current page
        selected = default

    if selected != current:
        dest = _ROUTE_MAP.get(selected)
        if dest:
            try:
                st.switch_page(dest)
            except Exception:
                pass


def _ROUND_TRIP_ORDER():
    # Order of tabs in the bar
    return ["Home", "Dream History", "Dream Insights", "Dream Logs", "Settings"]


# ---------- Card helpers ----------
def kpi_card(title: str, value: str, delta: str, col=None):
    target = col if col else st
    with target.container():
        st.markdown(f"""
        <div style="
          background: rgba(255,255,255,.02);
          border: 1px solid rgba(255,255,255,.08);
          border-radius: 16px; padding: 18px;">
          <div style="font-size:13px; opacity:.75;">{title}</div>
          <div style="font-size:28px; font-weight:800;">{value}</div>
          <div style="font-size:12px; font-weight:700; opacity:.8;">{delta}</div>
        </div>
        """, unsafe_allow_html=True)


def card(title: str, body_fn, col=None):
    target = col if col else st
    with target.container():
        st.markdown(
            '<div style="background:rgba(255,255,255,.02);'
            'border:1px solid rgba(255,255,255,.08);border-radius:16px; padding:18px;">',
            unsafe_allow_html=True
        )
        st.markdown(f'<div style="font-size:20px; font-weight:800; margin-bottom:8px;">{title}</div>',
                    unsafe_allow_html=True)
        body_fn()
        st.markdown("</div>", unsafe_allow_html=True)
