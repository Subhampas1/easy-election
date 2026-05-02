"""
pages.py — Streamlit Page Renderers with Multi-Language Support

Each public function renders one page/tab of the Citizen Election
Assistant. All UI text uses the ``t()`` helper for i18n.
All Google Cloud services (Logging, Storage, Maps) are actively used.
"""

from typing import Optional

import streamlit as st

from src.logic.election_engine import (
    generate_roadmap,
    get_evm_candidates,
    get_states,
    simulate_ballot,
    check_myth,
    get_election_myths,
    get_required_documents,
)
from src.services.cloud_logging_service import log_user_action, get_logger
from src.services.cloud_storage_service import list_available_resources
from src.services.google_maps_service import (
    get_polling_station_map_url,
    find_polling_stations,
    get_map_fallback_message,
)
from src.utils.translations import t


# ── party card data for the visual ballot ──────────────────────────
PARTY_SYMBOLS: list[dict[str, str]] = [
    {"symbol": "🪷", "name": "Party A", "candidate": "Candidate Alpha", "color": "#f59e0b"},
    {"symbol": "✋", "name": "Party B", "candidate": "Candidate Beta", "color": "#38bdf8"},
    {"symbol": "🌾", "name": "Party C", "candidate": "Candidate Gamma", "color": "#a78bfa"},
    {"symbol": "🚲", "name": "Party D", "candidate": "Candidate Delta", "color": "#14b8a6"},
    {"symbol": "🚫", "name": "NOTA", "candidate": "None Of The Above", "color": "#94a3b8"},
]


def render_home_page(lang: str = "en") -> None:
    """Render the home / landing page with hero section, stats, and feature cards."""

    st.markdown(f'<p class="hero-title">{t("hero_title", lang)}</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="hero-desc">{t("hero_desc", lang)}</p>', unsafe_allow_html=True)

    # ── stats ──
    st.markdown(
        f"""
        <div class="stat-grid">
            <div class="stat-box"><div class="stat-val">96.88 Cr</div><div class="stat-lbl">{t("registered_voters", lang)}</div></div>
            <div class="stat-box"><div class="stat-val">10.5 L</div><div class="stat-lbl">{t("polling_stations", lang)}</div></div>
            <div class="stat-box"><div class="stat-val">543</div><div class="stat-lbl">{t("lok_sabha", lang)}</div></div>
            <div class="stat-box"><div class="stat-val">28 + 8</div><div class="stat-lbl">{t("states_uts", lang)}</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── how voting works — visual process flow ──
    st.markdown(f"## {t('how_voting_works', lang)}")
    st.markdown(
        f"""
        <div class="process-flow">
            <div class="flow-step"><div class="flow-icon">📋</div><div class="flow-label">{t("step_register", lang)}</div><div class="flow-sub">Form 6 / NVSP</div></div>
            <div class="flow-arrow">→</div>
            <div class="flow-step"><div class="flow-icon">🪪</div><div class="flow-label">{t("step_voter_id", lang)}</div><div class="flow-sub">EPIC / e-EPIC</div></div>
            <div class="flow-arrow">→</div>
            <div class="flow-step"><div class="flow-icon">📍</div><div class="flow-label">{t("step_find_booth", lang)}</div><div class="flow-sub">Voter Helpline</div></div>
            <div class="flow-arrow">→</div>
            <div class="flow-step"><div class="flow-icon">🗳️</div><div class="flow-label">{t("step_cast_vote", lang)}</div><div class="flow-sub">EVM + VVPAT</div></div>
            <div class="flow-arrow">→</div>
            <div class="flow-step"><div class="flow-icon">✅</div><div class="flow-label">{t("step_get_inked", lang)}</div><div class="flow-sub">Left Index Finger</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── feature cards ──
    st.markdown(f"## {t('what_you_can_do', lang)}")
    cols = st.columns(3)
    cards = [
        ("🗺️", t("nav_roadmap", lang).replace("🗺️ ", ""), t("feat_roadmap_desc", lang)),
        ("🗳️", t("nav_ballot", lang).replace("🗳️ ", ""), t("feat_ballot_desc", lang)),
        ("🔍", t("nav_myth", lang).replace("🔍 ", ""), t("feat_myth_desc", lang)),
    ]
    for col, (icon, title, desc) in zip(cols, cards):
        with col:
            st.markdown(
                f'<div class="feat-card"><h3>{icon} {title}</h3><p>{desc}</p></div>',
                unsafe_allow_html=True,
            )

    # ── helpful icon cards ──
    st.markdown(f"## {t('essential_info', lang)}")
    st.markdown(
        f"""
        <div class="icon-card-grid">
            <div class="icon-card"><span class="ic-icon">🔞</span><div class="ic-title">{t("min_voting_age", lang)}</div><div class="ic-desc">{t("min_age_desc", lang)}</div></div>
            <div class="icon-card"><span class="ic-icon">🪪</span><div class="ic-title">{t("accepted_ids", lang)}</div><div class="ic-desc">{t("accepted_ids_desc", lang)}</div></div>
            <div class="icon-card"><span class="ic-icon">📞</span><div class="ic-title">{t("helpline_1950", lang)}</div><div class="ic-desc">{t("helpline_desc", lang)}</div></div>
            <div class="icon-card"><span class="ic-icon">🔒</span><div class="ic-title">{t("secret_ballot", lang)}</div><div class="ic-desc">{t("secret_ballot_desc", lang)}</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── polling station lookup (Google Maps) ──
    st.markdown("## 📍 Find Your Polling Station")
    pin_col, map_col = st.columns([1, 2])
    with pin_col:
        pin_code: str = st.text_input("Enter your PIN code", value="110001", key="pin_input", max_chars=6)
        if st.button("🔍 Find Stations", key="find_station_btn", use_container_width=True):
            log_user_action("polling_station_search", {"pin_code": pin_code})
            stations = find_polling_stations(pin_code)
            for station in stations:
                st.markdown(
                    f'<div class="feat-card"><h3>📍 {station["name"]}</h3>'
                    f'<p>{station["address"]}<br>'
                    f'<strong>Distance:</strong> {station["distance"]}</p></div>',
                    unsafe_allow_html=True,
                )
    with map_col:
        map_url: str = get_polling_station_map_url()
        fallback: str = get_map_fallback_message()
        if fallback:
            st.caption(fallback)
        st.image(map_url, use_container_width=True)

    # ── election resources (Google Cloud Storage) ──
    st.markdown("## 📚 Election Resources")
    resources = list_available_resources()
    res_cols = st.columns(3)
    for i, res in enumerate(resources[:6]):
        with res_cols[i % 3]:
            st.markdown(
                f'<div class="feat-card">'
                f'<h3>📄 {res["title"]}</h3>'
                f'<p style="font-size:0.85rem;">{res["description"]}</p>'
                f'<p style="color:#64748b;font-size:0.75rem;">Size: {res["size"]}</p>'
                f'<a href="{res["url"]}" target="_blank" style="color:#38bdf8;font-size:0.85rem;">⬇️ Download</a>'
                f'</div>',
                unsafe_allow_html=True,
            )

def render_roadmap_page(lang: str = "en") -> None:
    """Render the Election Roadmap page with personalized checklist."""

    st.markdown(f"# {t('nav_roadmap', lang)}")
    st.markdown(f'<p class="hero-desc">{t("hero_desc", lang)}</p>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        state: str = st.selectbox(t("select_state", lang), get_states(), key="roadmap_state")
    with col2:
        age: int = st.number_input(t("your_age", lang), min_value=1, max_value=120, value=18, step=1, key="roadmap_age")

    if st.button(t("generate_roadmap", lang), key="roadmap_btn", use_container_width=True):
        log_user_action("roadmap_page_submit", {"state": state, "age": age, "lang": lang})
        with st.spinner("..."):
            result: dict = generate_roadmap(state, age)

        if not result["eligible"]:
            st.warning(f"⏳ {result['title']}")
        else:
            st.success(f"✅ {result['title']}")

        st.markdown(f"## {t('your_checklist', lang)}")
        for step in result["steps"]:
            st.markdown(
                f'<div class="step-item"><div class="step-num">{step["step"]}</div>'
                f'<div class="step-body"><strong>{step["action"]}</strong>'
                f'<div class="step-detail">{step["detail"]}</div></div></div>',
                unsafe_allow_html=True,
            )

        st.markdown(f"## {t('required_docs', lang)}")
        docs: dict = result["documents"]
        for category, items in docs.items():
            with st.expander(f"📁 {category}"):
                for item in items:
                    st.markdown(f"- {item}")

        st.markdown(f"## {t('helpful_tips', lang)}")
        for tip_text in result["tips"]:
            st.markdown(f'<div class="tip-box">💡 {tip_text}</div>', unsafe_allow_html=True)

        if result["state_info"]:
            st.markdown(f"## {t('state_specific_info', lang)}")
            info = result["state_info"]
            st.markdown(
                f'<div class="feat-card"><h3>📌 {state}</h3>'
                f'<p><strong>{t("helpline_label", lang)}:</strong> {info.get("helpline", "N/A")}<br>'
                f'<strong>{t("website_label", lang)}:</strong> <a href="{info.get("website", "#")}" target="_blank" style="color:#38bdf8;">{info.get("website", "N/A")}</a><br>'
                f'<strong>{t("note_label", lang)}:</strong> {info.get("note", "—")}</p></div>',
                unsafe_allow_html=True,
            )


def render_ballot_page(lang: str = "en") -> None:
    """Render the Ballot Simulator page with interactive party cards."""

    st.markdown(f"# {t('nav_ballot', lang)}")
    st.markdown(f'<p class="hero-desc">{t("hero_desc", lang)}</p>', unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="process-flow">
            <div class="flow-step"><div class="flow-icon">🪪</div><div class="flow-label">{t("evm_verify_id", lang)}</div></div>
            <div class="flow-arrow">→</div>
            <div class="flow-step"><div class="flow-icon">☝️</div><div class="flow-label">{t("evm_press_button", lang)}</div></div>
            <div class="flow-arrow">→</div>
            <div class="flow-step"><div class="flow-icon">🔔</div><div class="flow-label">{t("evm_beep_light", lang)}</div></div>
            <div class="flow-arrow">→</div>
            <div class="flow-step"><div class="flow-icon">🧾</div><div class="flow-label">{t("evm_vvpat_slip", lang)}</div></div>
            <div class="flow-arrow">→</div>
            <div class="flow-step"><div class="flow-icon">✅</div><div class="flow-label">{t("evm_vote_recorded", lang)}</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown(f"### {t('choose_candidate', lang)}")

    candidates: list[str] = get_evm_candidates()
    cols = st.columns(len(PARTY_SYMBOLS))

    if "ballot_selected" not in st.session_state:
        st.session_state.ballot_selected = None

    for i, (col, party) in enumerate(zip(cols, PARTY_SYMBOLS)):
        with col:
            is_selected: bool = st.session_state.ballot_selected == i
            border_color: str = party["color"] if is_selected else "#334155"
            check_display: str = "flex" if is_selected else "none"
            nota_class: str = "nota-card" if party["name"] == "NOTA" else ""

            st.markdown(
                f'<div class="party-card {nota_class}" '
                f'style="border-color: {border_color}; '
                f'{"box-shadow: 0 0 24px " + party["color"] + "40;" if is_selected else ""}">'
                f'<div class="check-mark" style="display:{check_display};background:{party["color"]};">✓</div>'
                f'<span class="party-symbol">{party["symbol"]}</span>'
                f'<span class="party-name">{party["name"]}</span>'
                f'<span class="party-candidate">{party["candidate"]}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
            if st.button(f"{t('select_party', lang)} {party['name']}", key=f"party_{i}", use_container_width=True):
                st.session_state.ballot_selected = i
                st.rerun()

    st.markdown("---")

    if st.session_state.ballot_selected is not None:
        selected_party = PARTY_SYMBOLS[st.session_state.ballot_selected]
        st.markdown(
            f'<div class="evm-machine"><div class="evm-title">{t("evm_title", lang)}</div>'
            f'<div class="evm-screen"><div style="color:#64748b;font-size:0.75rem;margin-bottom:4px;">{t("evm_your_selection", lang)}</div>'
            f'<div style="font-size:2rem;margin-bottom:4px;">{selected_party["symbol"]}</div>'
            f'<div class="evm-selected-name">{selected_party["name"]} — {selected_party["candidate"]}</div></div>'
            f'<div class="evm-beep">{t("evm_ready", lang)}</div></div>',
            unsafe_allow_html=True,
        )

        if st.button(t("cast_vote", lang), key="cast_vote_btn", use_container_width=True):
            log_user_action("ballot_page_cast", {"candidate_index": st.session_state.ballot_selected, "lang": lang})
            with st.spinner("..."):
                result: dict = simulate_ballot(st.session_state.ballot_selected, candidates)

            if result["success"]:
                st.balloons()
                st.success(f"{t('vote_recorded_for', lang)}: **{result['selected_candidate']}**")
                st.markdown(
                    f'<div class="vvpat-slip"><div class="vvpat-label">{t("vvpat_label", lang)}</div>'
                    f'<div style="font-size:2rem;margin:0.5rem 0;">{selected_party["symbol"]}</div>'
                    f'<div class="vvpat-candidate">{result["selected_candidate"]}</div>'
                    f'<div class="vvpat-time">{t("vvpat_display_time", lang)}</div>'
                    f'<div style="margin-top:0.75rem;"><span class="badge badge-true">✓ VVPAT MATCHED</span></div></div>',
                    unsafe_allow_html=True,
                )
                with st.expander(t("evm_how_recorded", lang)):
                    st.markdown(result["evm_explanation"])
                with st.expander(t("vvpat_how_verified", lang)):
                    st.markdown(result["vvpat_explanation"])
            else:
                st.error(result["error"])
    else:
        st.info(t("select_party_prompt", lang))


def render_mythbuster_page(lang: str = "en") -> None:
    """Render the Myth Buster page with search and browsable myths."""

    st.markdown(f"# {t('nav_myth', lang)}")
    st.markdown(f'<p class="hero-desc">{t("hero_desc", lang)}</p>', unsafe_allow_html=True)

    claim: str = st.text_input(
        t("enter_claim", lang),
        placeholder="e.g., Can EVMs be hacked?",
        key="myth_input",
    )

    if st.button(t("check_claim", lang), key="myth_check_btn", use_container_width=True):
        log_user_action("myth_page_check", {"claim": claim, "lang": lang})
        with st.spinner("..."):
            result: dict = check_myth(claim)

        if result["found"]:
            verdict: str = result["verdict"]
            badge_cls: str = "badge-false"
            if verdict == "TRUE":
                badge_cls = "badge-true"
            elif "PARTIAL" in verdict:
                badge_cls = "badge-partial"
            st.markdown(
                f'<div class="myth-card"><span class="badge {badge_cls}">{verdict}</span>'
                f'<h4>"{result["myth"]}"</h4><p>{result["explanation"]}</p>'
                f'<div class="myth-source">📚 Source: {result["source"]}</div></div>',
                unsafe_allow_html=True,
            )
        else:
            st.warning(result["explanation"])

    st.markdown("---")
    st.markdown(f"## {t('browse_myths', lang)}")

    myths: list[dict[str, str]] = get_election_myths()
    for myth_entry in myths:
        verdict: str = myth_entry["verdict"]
        badge_cls: str = "badge-false"
        if verdict == "TRUE":
            badge_cls = "badge-true"
        elif "PARTIAL" in verdict:
            badge_cls = "badge-partial"
        with st.expander(f'{myth_entry["myth"]}'):
            st.markdown(f'<span class="badge {badge_cls}">{verdict}</span>', unsafe_allow_html=True)
            st.markdown(myth_entry["explanation"])
            st.caption(f"📚 Source: {myth_entry['source']}")
