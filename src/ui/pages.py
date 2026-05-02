"""
pages.py — Streamlit Page Renderers

Each public function renders one page/tab of the Citizen Election
Assistant. The module imports only from the ``src`` package — never
directly from engine.py or prompts.py.
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
from src.services.cloud_logging_service import log_user_action


# ── party card data for the visual ballot ──────────────────────────
PARTY_SYMBOLS: list[dict[str, str]] = [
    {"symbol": "🪷", "name": "Party A", "candidate": "Candidate Alpha", "color": "#f59e0b"},
    {"symbol": "✋", "name": "Party B", "candidate": "Candidate Beta", "color": "#38bdf8"},
    {"symbol": "🌾", "name": "Party C", "candidate": "Candidate Gamma", "color": "#a78bfa"},
    {"symbol": "🚲", "name": "Party D", "candidate": "Candidate Delta", "color": "#14b8a6"},
    {"symbol": "🚫", "name": "NOTA", "candidate": "None Of The Above", "color": "#94a3b8"},
]


def render_home_page() -> None:
    """Render the home / landing page with hero section, stats, and feature cards."""

    st.markdown('<p class="hero-title">Citizen Election<br>Assistant 🇮🇳</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="hero-desc">'
        "Your personal guide to India's democratic process — from registration to casting "
        "your first vote. Built for first-time voters, students, and every citizen who "
        "wants to make their voice count."
        "</p>",
        unsafe_allow_html=True,
    )

    # ── stats ──
    st.markdown(
        """
        <div class="stat-grid">
            <div class="stat-box"><div class="stat-val">96.88 Cr</div><div class="stat-lbl">Registered Voters</div></div>
            <div class="stat-box"><div class="stat-val">10.5 L</div><div class="stat-lbl">Polling Stations</div></div>
            <div class="stat-box"><div class="stat-val">543</div><div class="stat-lbl">Lok Sabha Seats</div></div>
            <div class="stat-box"><div class="stat-val">28 + 8</div><div class="stat-lbl">States & UTs</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── how voting works — visual process flow ──
    st.markdown("## How Voting Works")
    st.markdown(
        """
        <div class="process-flow">
            <div class="flow-step"><div class="flow-icon">📋</div><div class="flow-label">Register</div><div class="flow-sub">Form 6 / NVSP</div></div>
            <div class="flow-arrow">→</div>
            <div class="flow-step"><div class="flow-icon">🪪</div><div class="flow-label">Get Voter ID</div><div class="flow-sub">EPIC / e-EPIC</div></div>
            <div class="flow-arrow">→</div>
            <div class="flow-step"><div class="flow-icon">📍</div><div class="flow-label">Find Booth</div><div class="flow-sub">Voter Helpline</div></div>
            <div class="flow-arrow">→</div>
            <div class="flow-step"><div class="flow-icon">🗳️</div><div class="flow-label">Cast Vote</div><div class="flow-sub">EVM + VVPAT</div></div>
            <div class="flow-arrow">→</div>
            <div class="flow-step"><div class="flow-icon">✅</div><div class="flow-label">Get Inked</div><div class="flow-sub">Left Index Finger</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── feature cards ──
    st.markdown("## What You Can Do Here")
    cols = st.columns(3)
    cards = [
        ("🗺️", "Election Roadmap", "Get a personalized step-by-step checklist for voter registration tailored to your state and age."),
        ("🗳️", "Ballot Simulator", "Experience how the EVM and VVPAT work in a realistic, guided simulation."),
        ("🔍", "Myth Buster", "Verify election-related claims with fact-checked verdicts and official sources."),
    ]
    for col, (icon, title, desc) in zip(cols, cards):
        with col:
            st.markdown(
                f'<div class="feat-card">'
                f'<h3>{icon} {title}</h3>'
                f'<p>{desc}</p>'
                f'</div>',
                unsafe_allow_html=True,
            )

    # ── helpful icon cards ──
    st.markdown("## Essential Election Info")
    st.markdown(
        """
        <div class="icon-card-grid">
            <div class="icon-card"><span class="ic-icon">🔞</span><div class="ic-title">Min. Voting Age</div><div class="ic-desc">You must be 18+ on the qualifying date to register as a voter.</div></div>
            <div class="icon-card"><span class="ic-icon">🪪</span><div class="ic-title">12 Accepted IDs</div><div class="ic-desc">Voter ID, Aadhaar, Passport, PAN Card, Driving License & more.</div></div>
            <div class="icon-card"><span class="ic-icon">📞</span><div class="ic-title">Helpline: 1950</div><div class="ic-desc">Call the National Voter Helpline for any election-related query.</div></div>
            <div class="icon-card"><span class="ic-icon">🔒</span><div class="ic-title">Secret Ballot</div><div class="ic-desc">Your vote is 100% secret. No one can see whom you voted for.</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_roadmap_page() -> None:
    """Render the Election Roadmap page with personalized checklist."""

    st.markdown("# 🗺️ Election Roadmap")
    st.markdown(
        '<p class="hero-desc">Get your personalized step-by-step guide to becoming a registered voter.</p>',
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        state: str = st.selectbox("Select your State / UT", get_states(), key="roadmap_state")
    with col2:
        age: int = st.number_input("Your Age", min_value=1, max_value=120, value=18, step=1, key="roadmap_age")

    if st.button("🚀 Generate My Roadmap", key="roadmap_btn", use_container_width=True):
        log_user_action("roadmap_page_submit", {"state": state, "age": age})
        with st.spinner("Building your personalized roadmap…"):
            result: dict = generate_roadmap(state, age)

        if not result["eligible"]:
            st.warning(f"⏳ {result['title']}")
        else:
            st.success(f"✅ {result['title']}")

        # ── steps ──
        st.markdown("## 📋 Your Checklist")
        for step in result["steps"]:
            st.markdown(
                f'<div class="step-item">'
                f'<div class="step-num">{step["step"]}</div>'
                f'<div class="step-body">'
                f'<strong>{step["action"]}</strong>'
                f'<div class="step-detail">{step["detail"]}</div>'
                f'</div></div>',
                unsafe_allow_html=True,
            )

        # ── documents ──
        st.markdown("## 📄 Required Documents")
        docs: dict = result["documents"]
        for category, items in docs.items():
            with st.expander(f"📁 {category}"):
                for item in items:
                    st.markdown(f"- {item}")

        # ── tips ──
        st.markdown("## 💡 Helpful Tips")
        for tip in result["tips"]:
            st.markdown(f'<div class="tip-box">💡 {tip}</div>', unsafe_allow_html=True)

        # ── state info ──
        if result["state_info"]:
            st.markdown("## 🏛️ State-Specific Info")
            info = result["state_info"]
            st.markdown(
                f'<div class="feat-card">'
                f'<h3>📌 {state}</h3>'
                f'<p><strong>Helpline:</strong> {info.get("helpline", "N/A")}<br>'
                f'<strong>Website:</strong> <a href="{info.get("website", "#")}" target="_blank" style="color:#38bdf8;">{info.get("website", "N/A")}</a><br>'
                f'<strong>Note:</strong> {info.get("note", "—")}</p>'
                f'</div>',
                unsafe_allow_html=True,
            )


def render_ballot_page() -> None:
    """Render the Ballot Simulator page with interactive party cards."""

    st.markdown("# 🗳️ Ballot Simulator")
    st.markdown(
        '<p class="hero-desc">Experience how India\'s Electronic Voting Machine (EVM) and VVPAT work in this guided simulation.</p>',
        unsafe_allow_html=True,
    )

    # ── visual EVM process ──
    st.markdown(
        """
        <div class="process-flow">
            <div class="flow-step"><div class="flow-icon">🪪</div><div class="flow-label">Verify ID</div></div>
            <div class="flow-arrow">→</div>
            <div class="flow-step"><div class="flow-icon">☝️</div><div class="flow-label">Press Button</div></div>
            <div class="flow-arrow">→</div>
            <div class="flow-step"><div class="flow-icon">🔔</div><div class="flow-label">Beep + Light</div></div>
            <div class="flow-arrow">→</div>
            <div class="flow-step"><div class="flow-icon">🧾</div><div class="flow-label">VVPAT Slip</div></div>
            <div class="flow-arrow">→</div>
            <div class="flow-step"><div class="flow-icon">✅</div><div class="flow-label">Vote Recorded</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown("### Choose Your Candidate")
    st.markdown("*Tap a party card to select your candidate — just like in a real polling booth.*")

    # ── party card selection ──
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
            if st.button(f"Select {party['name']}", key=f"party_{i}", use_container_width=True):
                st.session_state.ballot_selected = i
                st.rerun()

    st.markdown("---")

    # ── cast vote button ──
    if st.session_state.ballot_selected is not None:
        selected_party = PARTY_SYMBOLS[st.session_state.ballot_selected]
        st.markdown(
            f'<div class="evm-machine">'
            f'<div class="evm-title">Electronic Voting Machine</div>'
            f'<div class="evm-screen">'
            f'<div style="color:#64748b;font-size:0.75rem;margin-bottom:4px;">YOUR SELECTION</div>'
            f'<div style="font-size:2rem;margin-bottom:4px;">{selected_party["symbol"]}</div>'
            f'<div class="evm-selected-name">{selected_party["name"]} — {selected_party["candidate"]}</div>'
            f'</div>'
            f'<div class="evm-beep">🟢 Ready to cast</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        if st.button("🗳️ CAST YOUR VOTE", key="cast_vote_btn", use_container_width=True):
            log_user_action("ballot_page_cast", {"candidate_index": st.session_state.ballot_selected})
            with st.spinner("Recording your vote…"):
                result: dict = simulate_ballot(st.session_state.ballot_selected, candidates)

            if result["success"]:
                st.balloons()
                st.success(f"✅ Vote recorded for: **{result['selected_candidate']}**")

                # VVPAT slip
                st.markdown(
                    f'<div class="vvpat-slip">'
                    f'<div class="vvpat-label">VVPAT Verification Slip</div>'
                    f'<div style="font-size:2rem;margin:0.5rem 0;">{selected_party["symbol"]}</div>'
                    f'<div class="vvpat-candidate">{result["selected_candidate"]}</div>'
                    f'<div class="vvpat-time">⏱️ Displayed for 7 seconds</div>'
                    f'<div style="margin-top:0.75rem;"><span class="badge badge-true">✓ VVPAT MATCHED</span></div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

                with st.expander("📖 How the EVM Recorded Your Vote"):
                    st.markdown(result["evm_explanation"])
                with st.expander("🧾 How VVPAT Verified Your Vote"):
                    st.markdown(result["vvpat_explanation"])
            else:
                st.error(result["error"])
    else:
        st.info("☝️ Select a party card above to start the simulation.")


def render_mythbuster_page() -> None:
    """Render the Myth Buster page with search and browsable myths."""

    st.markdown("# 🔍 Myth Buster")
    st.markdown(
        '<p class="hero-desc">Verify election-related claims with fact-checked verdicts from official sources.</p>',
        unsafe_allow_html=True,
    )

    claim: str = st.text_input(
        "Enter a claim to verify",
        placeholder="e.g., Can EVMs be hacked?",
        key="myth_input",
    )

    if st.button("🔍 Check This Claim", key="myth_check_btn", use_container_width=True):
        log_user_action("myth_page_check", {"claim": claim})
        with st.spinner("Fact-checking…"):
            result: dict = check_myth(claim)

        if result["found"]:
            verdict: str = result["verdict"]
            badge_cls: str = "badge-false"
            if verdict == "TRUE":
                badge_cls = "badge-true"
            elif "PARTIAL" in verdict:
                badge_cls = "badge-partial"

            st.markdown(
                f'<div class="myth-card">'
                f'<span class="badge {badge_cls}">{verdict}</span>'
                f'<h4>"{result["myth"]}"</h4>'
                f'<p>{result["explanation"]}</p>'
                f'<div class="myth-source">📚 Source: {result["source"]}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        else:
            st.warning(result["explanation"])

    # ── browse all myths ──
    st.markdown("---")
    st.markdown("## 📚 Browse All Election Myths")

    myths: list[dict[str, str]] = get_election_myths()
    for myth_entry in myths:
        verdict: str = myth_entry["verdict"]
        badge_cls: str = "badge-false"
        if verdict == "TRUE":
            badge_cls = "badge-true"
        elif "PARTIAL" in verdict:
            badge_cls = "badge-partial"

        with st.expander(f'{myth_entry["myth"]}'):
            st.markdown(
                f'<span class="badge {badge_cls}">{verdict}</span>',
                unsafe_allow_html=True,
            )
            st.markdown(myth_entry["explanation"])
            st.caption(f"📚 Source: {myth_entry['source']}")
