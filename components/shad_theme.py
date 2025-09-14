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
          {"[data-testid='stSidebar'],[data-testid='stSidebarNav']{display:none !important;}"
            "[data-testid='stToolbar'] button[kind='header']{display:none !important;}"
            ".main .block-container{padding-top:0.75rem; max-width:1200px;}" if hide_sidebar else ""}

          /* ======== Light Theme Tokens (shadcn-like) ======== */
          :root {{
            --bg: #ffffff;
            --muted: #f8fafc;            /* card fill */
            --muted-2: #eef2f7;          /* subtle fill */
            --border: #e5e7eb;           /* slate-200 */
            --text: #0f172a;             /* slate-900 */
            --text-muted: #64748b;       /* slate-500 */
            --accent: #111827;           /* near-black accent */
            --ring: rgba(17,24,39,.08);
            --shadow: 0 1px 2px rgba(16,24,40,0.08), 0 2px 8px rgba(16,24,40,0.06);
            --radius: 14px;
          }}

          html, body {{ background: var(--bg); color: var(--text); }}

          /* Header block */
          .nm-header {{
            background: var(--muted);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 18px 16px;
            margin-bottom: 12px;
            box-shadow: var(--shadow);
          }}
          .nm-title {{ font-weight: 800; font-size: 1.25rem; margin: 2px 0; color: var(--text); }}
          .nm-sub   {{ color: var(--text-muted); font-size: 0.95rem; }}

          /* Tabs (shadcn tabs already light; just spacing) */
          .stTabs [data-baseweb="tab-list"] {{ gap: 6px; }}

          /* Generic card */
          .nm-card {{
            background: var(--muted);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 18px;
            box-shadow: var(--shadow);
          }}

          /* KPI typography */
          .nm-kpi-title {{ font-size:13px; color: var(--text-muted); }}
          .nm-kpi-value {{ font-size:28px; font-weight:800; color: var(--text); }}
          .nm-kpi-delta {{ font-size:12px; font-weight:700; color: var(--text-muted); }}
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
        st.markdown(
            f"""
            <div class="nm-card">
              <div class="nm-kpi-title">{title}</div>
              <div class="nm-kpi-value">{value}</div>
              <div class="nm-kpi-delta">{delta}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

def card(title: str, body_fn, col=None):
    target = col if col else st
    with target.container():
        st.markdown('<div class="nm-card">', unsafe_allow_html=True)
        st.markdown(f'<div style="font-size:20px; font-weight:800; margin-bottom:8px; color:var(--text);">{title}</div>', unsafe_allow_html=True)
        body_fn()
        st.markdown("</div>", unsafe_allow_html=True)

