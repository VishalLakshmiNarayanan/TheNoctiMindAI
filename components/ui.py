# components/ui.py
from __future__ import annotations
import streamlit as st

# shadcn-ui component
try:
    import streamlit_shadcn_ui as ui
except Exception:
    ui = None  # we'll degrade gracefully

from modules.auth import user_greeting, logout_button


def _inject_base_css(hide_sidebar: bool):
    st.markdown(
        f"""
        <style>
          {"[data-testid='stSidebar'],[data-testid='stSidebarNav']{{display:none;}}" if hide_sidebar else ""}
          .main .block-container {{ padding-top: 0.75rem; max-width: 1200px; }}

          /* shadcn-like cards / header feel */
          .nm-header {{
            background: rgba(255,255,255,.02);
            border: 1px solid rgba(255,255,255,.08);
            border-radius: 16px;
            padding: 18px 16px;
            margin-bottom: 12px;
          }}
          .nm-title {{ font-weight: 800; font-size: 1.25rem; margin: 2px 0; }}
          .nm-sub   {{ opacity: .75; font-size: 0.95rem; }}

          .nm-right {{
            display: flex; gap: .5rem; align-items: center; justify-content: flex-end;
          }}

          /* fallback pills (if shadcn component missing) */
          .navpill {{
            display:inline-flex; align-items:center; gap:.5rem;
            padding:.5rem .8rem; border-radius:999px;
            border:1px solid rgba(255,255,255,.12);
            background: rgba(255,255,255,.02); color:#e6e6ef; text-decoration:none;
            font-weight:600; font-size:.95rem;
          }}
          .navpill:hover {{ background: rgba(255,255,255,.06); border-color: rgba(255,255,255,.2); }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _header():
    """Hero header like the screenshot: title, subtext, CTA buttons on the right."""
    st.markdown('<div class="nm-header">', unsafe_allow_html=True)
    c1, csp, c2 = st.columns([0.66, 0.02, 0.32])
    with c1:
        st.markdown('<div class="nm-title">Streamlit Shadcn UI</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="nm-sub">A Streamlit component library for building beautiful apps easily. '
            'Bring the power of <b>shadcn/ui</b> to your Streamlit apps!</div>',
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown('<div class="nm-right">', unsafe_allow_html=True)
        if ui:
            ui.button(text="Get Started", key="nm_get_started", variant="default")
            ui.button(text="Github", key="nm_github", variant="secondary")
        else:
            st.link_button("Get Started", "#")
            st.link_button("Github", "#")
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


def _tabs_nav():
    """
    Shadcn-style tabs that navigate to your pages.
    We map tab selection -> st.switch_page for a clean UX.
    """
    if ui:
        selected = ui.tabs(
            options=["Overview", "Analytics", "Reports", "Notifications"],
            default_value="Overview",
            key="nm_tabs",
        )
    else:
        # Fallback if component isn't installed
        cols = st.columns(4)
        labels = ["Overview", "Analytics", "Reports", "Notifications"]
        selected = "Overview"
        for i, lab in enumerate(labels):
            with cols[i]:
                if st.button(lab, use_container_width=True):
                    selected = lab

    # Route to pages (keep these labels aligned with your app structure)
    # Overview -> app.py (root); Analytics -> History; Reports -> Insights; Notifications -> Log
    if "route_guard" not in st.session_state:
        st.session_state["route_guard"] = False  # to avoid infinite rerun loops

    route_map = {
        "Overview": "app.py",
        "Analytics": "pages/2_📊_History.py",
        "Reports": "pages/3_🧭_Insights.py",
        "Notifications": "pages/1_📘_Log_a_Dream.py",
    }

    # Only switch if the current script isn't already that page
    target = route_map.get(selected)
    if target:
        # Heuristic: if we're not on the target page, allow switch
        # You can also use query params or session flags to refine this
        if not st.session_state["route_guard"]:
            st.session_state["route_guard"] = True
            try:
                st.switch_page(target)
            except Exception:
                # If switch_page not available or same page, ignore
                pass
        else:
            # Reset guard for next user interaction cycle
            st.session_state["route_guard"] = False


def render_top_nav(hide_sidebar: bool = True):
    """
    Drop-in replacement: renders a shadcn-style header + tabbed nav + user info block.
    """
    _inject_base_css(hide_sidebar)

    # Header like screenshot
    _header()

    # Tabs row (Overview / Analytics / Reports / Notifications)
    _tabs_nav()

    # User greeting + logout (right aligned row)
    r1, r2 = st.columns([0.7, 0.3])
    with r2:
        user_greeting()
        logout_button()
