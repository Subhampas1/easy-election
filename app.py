"""
app.py — Citizen Election Assistant Entry Point

A thin Streamlit dispatcher that delegates all rendering to
``src.ui.pages`` and all logic to ``src.logic``. This module only
configures the page, injects CSS, and dispatches to the active tab.
"""

import streamlit as st

from src.ui.styles import inject_custom_css
from src.ui.pages import (
    render_home_page,
    render_roadmap_page,
    render_ballot_page,
    render_mythbuster_page,
)
from src.services.cloud_logging_service import get_logger, log_user_action


# ── page configuration (must be FIRST Streamlit call) ──
st.set_page_config(
    page_title="Citizen Election Assistant 🇮🇳",
    page_icon="🗳️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": (
            "**Citizen Election Assistant** — Your guide to India's "
            "democratic process. Built with ❤️ for every voter."
        ),
    },
)

# ── inject CSS design system ──
inject_custom_css()

# ── initialize logger ──
logger = get_logger()


# ── sidebar navigation ──
with st.sidebar:
    st.markdown("## 🇮🇳 Election Assistant")
    st.markdown("---")

    page: str = st.radio(
        "Navigate to",
        options=["🏠 Home", "🗺️ Roadmap", "🗳️ Ballot Sim", "🔍 Myth Buster"],
        key="nav_radio",
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown(
        '<div style="text-align:center;padding:0.5rem;">'
        '<p style="color:#64748b!important;font-size:0.75rem;margin:0;">'
        "Made with ❤️ for Indian Democracy<br>"
        "© 2026 Citizen Election Assistant"
        "</p></div>",
        unsafe_allow_html=True,
    )


# ── route to the active page ──
log_user_action("page_view", {"page": page})

if page == "🏠 Home":
    render_home_page()
elif page == "🗺️ Roadmap":
    render_roadmap_page()
elif page == "🗳️ Ballot Sim":
    render_ballot_page()
elif page == "🔍 Myth Buster":
    render_mythbuster_page()
else:
    render_home_page()
