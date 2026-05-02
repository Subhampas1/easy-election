import streamlit as st

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

from src.ui.styles import inject_custom_css
from src.ui.pages import (
    render_home_page,
    render_roadmap_page,
    render_ballot_page,
    render_mythbuster_page,
)
from src.services.cloud_logging_service import get_logger, log_user_action
from src.services.bigquery_service import track_event
from src.utils.translations import SUPPORTED_LANGUAGES, get_lang_code, t
from src.utils.accessibility import SKIP_NAV_HTML, SKIP_NAV_CSS
from src.utils.security import generate_csp_header, check_rate_limit, generate_csrf_token

# ── inject CSS design system + accessibility CSS ──
inject_custom_css()
st.markdown(SKIP_NAV_CSS, unsafe_allow_html=True)
st.markdown(SKIP_NAV_HTML, unsafe_allow_html=True)

# ── initialize logger ──
logger = get_logger()

# ── security: CSP header + CSRF token ──
csp_header: str = generate_csp_header()
st.markdown(
    f'<meta http-equiv="Content-Security-Policy" content="{csp_header}">',
    unsafe_allow_html=True,
)
if "csrf_token" not in st.session_state:
    st.session_state["csrf_token"] = generate_csrf_token()

# ── main content landmark ──
st.markdown('<div id="main-content" role="main" aria-label="Primary content">', unsafe_allow_html=True)


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

    # ── accessibility: high contrast toggle ──
    high_contrast: bool = st.toggle("High Contrast Mode", key="high_contrast_toggle", value=False)
    if high_contrast:
        st.markdown(
            '<script>document.body.classList.add("high-contrast");</script>',
            unsafe_allow_html=True,
        )

    st.markdown(
        f'<div style="text-align:center;padding:0.5rem;">'
        f'<p style="color:#64748b!important;font-size:0.75rem;margin:0;">'
        f'{t("footer", lang)}<br>'
        f"© 2026 Citizen Election Assistant"
        f"</p></div>",
        unsafe_allow_html=True,
    )


# ── rate limiting check ──
session_id: str = st.session_state.get("csrf_token", "default")[:16]
if not check_rate_limit(session_id):
    st.error("Too many requests. Please wait a moment before trying again.")
    st.stop()

# ── route to the active page ──
log_user_action("page_view", {"page": page, "lang": lang})
track_event("page_view", {"page": page, "lang": lang}, session_id)

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

# ── close main content landmark ──
st.markdown('</div>', unsafe_allow_html=True)
