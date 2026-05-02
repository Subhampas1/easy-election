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
from src.utils.translations import SUPPORTED_LANGUAGES, get_lang_code, t


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
    # ── branded header ──
    st.markdown(
        '<div class="sidebar-brand">'
        '<span class="sb-logo">🗳️</span>'
        '<span class="sb-title">Election Assistant</span>'
        '<span class="sb-sub">Government of India</span>'
        '</div>',
        unsafe_allow_html=True,
    )

    # ── language selector ──
    lang_name: str = st.selectbox(
        t("language", "en"),
        options=list(SUPPORTED_LANGUAGES.keys()),
        key="lang_select",
    )
    lang: str = get_lang_code(lang_name)
    st.session_state["lang"] = lang

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

    nav_options: list[str] = [
        t("nav_home", lang),
        t("nav_roadmap", lang),
        t("nav_ballot", lang),
        t("nav_myth", lang),
    ]

    page: str = st.radio(
        "Navigate",
        options=nav_options,
        key="nav_radio",
        label_visibility="collapsed",
    )

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
    st.markdown(
        f'<div style="text-align:center;padding:0.5rem;">'
        f'<p style="color:#64748b!important;font-size:0.75rem;margin:0;">'
        f'{t("footer", lang)}<br>'
        f"© 2026 Citizen Election Assistant"
        f"</p></div>",
        unsafe_allow_html=True,
    )


# ── route to the active page ──
log_user_action("page_view", {"page": page, "lang": lang})

if page == nav_options[0]:
    render_home_page(lang)
elif page == nav_options[1]:
    render_roadmap_page(lang)
elif page == nav_options[2]:
    render_ballot_page(lang)
elif page == nav_options[3]:
    render_mythbuster_page(lang)
else:
    render_home_page(lang)
