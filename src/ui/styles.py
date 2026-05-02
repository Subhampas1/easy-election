"""
styles.py — Centralized CSS Design System

All custom CSS for the Citizen Election Assistant is maintained here.
This module exports a single function ``inject_custom_css()`` that
injects the complete design system into the Streamlit app.
"""

import streamlit as st


def inject_custom_css() -> None:
    """Inject the complete custom CSS design system into Streamlit.

    This function should be called once at the top of the app, after
    ``st.set_page_config()``. It applies the dark glassmorphism theme,
    typography, button styles, card layouts, and accessibility features.
    """
    st.markdown(_CSS, unsafe_allow_html=True)


_CSS: str = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

html, body, .stApp, .stMarkdown, p, span, li, label, div {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}
.stApp {
    background: linear-gradient(160deg, #0b1120 0%, #101b30 40%, #0d1525 100%) !important;
}
.stApp > header { background: transparent !important; }
.stApp .stMarkdown p, .stApp .stMarkdown li, .stApp .stMarkdown span, .stApp label, .stApp .stMarkdown div {
    color: #e2e8f0 !important;
}
.stApp h1 { color: #ffffff !important; font-weight: 800 !important; letter-spacing: -0.03em; font-size: 2.2rem !important; }
.stApp h2 { color: #fbbf24 !important; font-weight: 700 !important; font-size: 1.5rem !important; margin-top: 1.5rem !important; }
.stApp h3 { color: #38bdf8 !important; font-weight: 600 !important; font-size: 1.2rem !important; }

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%) !important;
    border-right: 1px solid #334155 !important;
}
section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 { color: #fbbf24 !important; }
section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] li, section[data-testid="stSidebar"] span, section[data-testid="stSidebar"] label { color: #cbd5e1 !important; }

.stRadio label span, .stSelectbox label span, .stNumberInput label span, .stTextInput label span {
    color: #e2e8f0 !important; font-weight: 500 !important;
}
.stButton > button {
    background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%) !important;
    color: #000000 !important; font-weight: 700 !important; border: none !important;
    border-radius: 10px !important; padding: 0.65rem 1.5rem !important;
    font-size: 1rem !important; transition: all 0.2s ease !important; letter-spacing: 0.02em;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%) !important;
    transform: translateY(-1px); box-shadow: 0 6px 20px rgba(245, 158, 11, 0.3) !important;
}

.streamlit-expanderHeader { background: #1e293b !important; border: 1px solid #334155 !important; border-radius: 10px !important; color: #e2e8f0 !important; font-weight: 500 !important; }
.streamlit-expanderContent { background: #1e293b !important; border: 1px solid #334155 !important; border-top: none !important; color: #cbd5e1 !important; }
details { background: #1e293b !important; border: 1px solid #334155 !important; border-radius: 10px !important; margin-bottom: 0.5rem; overflow: hidden; }
details summary { color: #e2e8f0 !important; font-weight: 500 !important; padding: 0.85rem 1rem !important; display: flex !important; align-items: center !important; gap: 0px !important; cursor: pointer; list-style: none !important; }
details summary::-webkit-details-marker { display: none; }
details summary span[data-testid="stMarkdownContainer"] { color: #e2e8f0 !important; -webkit-text-fill-color: #e2e8f0 !important; }
details summary svg { flex-shrink: 0; width: 20px; height: 20px; color: #94a3b8 !important; }
details > div { color: #cbd5e1 !important; padding: 0 1rem 0.75rem 1rem; }

@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200');
[data-testid="stIconMaterial"] { font-family: 'Material Symbols Rounded' !important; font-weight: normal !important; font-style: normal !important; font-size: 24px !important; line-height: 1 !important; letter-spacing: normal !important; text-transform: none !important; display: inline-block !important; white-space: nowrap !important; word-wrap: normal !important; direction: ltr !important; -webkit-font-smoothing: antialiased !important; color: #94a3b8 !important; -webkit-text-fill-color: #94a3b8 !important; flex-shrink: 0 !important; width: 24px !important; height: 24px !important; overflow: hidden !important; }
[data-testid="stExpander"] summary > span:first-child { flex-shrink: 0 !important; display: flex !important; align-items: center !important; gap: 0 !important; }
[data-testid="stExpander"] [data-testid="stMarkdownContainer"] p { color: #e2e8f0 !important; -webkit-text-fill-color: #e2e8f0 !important; margin: 0 !important; }

.hero-title { font-size: 3rem; font-weight: 900; line-height: 1.15; background: linear-gradient(135deg, #f59e0b 0%, #38bdf8 60%, #a78bfa 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin-bottom: 0.5rem; }
.hero-desc { color: #94a3b8 !important; font-size: 1.1rem; line-height: 1.7; max-width: 650px; margin-bottom: 1.5rem; }
.stat-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem; margin: 1.5rem 0; }
.stat-box { background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); border: 1px solid #334155; border-radius: 14px; padding: 1.25rem; text-align: center; transition: all 0.25s ease; }
.stat-box:hover { border-color: #f59e0b; transform: translateY(-2px); box-shadow: 0 8px 24px rgba(245,158,11,0.12); }
.stat-val { font-size: 1.8rem; font-weight: 800; color: #fbbf24 !important; -webkit-text-fill-color: #fbbf24; }
.stat-lbl { font-size: 0.8rem; color: #64748b !important; -webkit-text-fill-color: #64748b; margin-top: 4px; text-transform: uppercase; letter-spacing: 0.05em; }

.feat-card { background: linear-gradient(145deg, #1e293b 0%, #162032 100%); border: 1px solid #334155; border-radius: 14px; padding: 1.5rem; height: 100%; transition: all 0.3s ease; }
.feat-card:hover { border-color: #38bdf8; box-shadow: 0 6px 20px rgba(56,189,248,0.1); transform: translateY(-2px); }
.feat-card h3 { color: #38bdf8 !important; -webkit-text-fill-color: #38bdf8; font-size: 1.15rem; margin-bottom: 0.5rem; }
.feat-card p { color: #94a3b8 !important; -webkit-text-fill-color: #94a3b8; font-size: 0.95rem; line-height: 1.6; }

.step-item { background: linear-gradient(135deg, #1e293b 0%, #162032 100%); border-left: 4px solid #14b8a6; border-radius: 0 12px 12px 0; padding: 1rem 1.25rem; margin: 0.6rem 0; display: flex; align-items: flex-start; gap: 12px; }
.step-num { flex-shrink: 0; width: 30px; height: 30px; background: #14b8a6; color: #000 !important; -webkit-text-fill-color: #000; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 0.85rem; }
.step-body strong { color: #f1f5f9 !important; -webkit-text-fill-color: #f1f5f9; font-size: 1rem; }
.step-body .step-detail { color: #94a3b8 !important; -webkit-text-fill-color: #94a3b8; font-size: 0.9rem; margin-top: 2px; line-height: 1.5; }

.tip-box { background: #1e293b; border: 1px solid #334155; border-radius: 10px; padding: 0.75rem 1rem; margin: 0.4rem 0; color: #e2e8f0 !important; -webkit-text-fill-color: #e2e8f0; font-size: 0.95rem; }

.vvpat-slip { background: linear-gradient(135deg, #1e293b, #162032); border: 2px solid #14b8a6; border-radius: 14px; padding: 2rem; text-align: center; max-width: 400px; margin: 1rem auto; }
.vvpat-label { font-size: 0.75rem; color: #64748b !important; -webkit-text-fill-color: #64748b; letter-spacing: 0.15em; text-transform: uppercase; }
.vvpat-candidate { font-size: 1.4rem; font-weight: 700; color: #fbbf24 !important; -webkit-text-fill-color: #fbbf24; margin: 0.75rem 0; }
.vvpat-time { font-size: 0.8rem; color: #64748b !important; -webkit-text-fill-color: #64748b; }

.badge { display: inline-block; padding: 5px 16px; border-radius: 999px; font-weight: 700; font-size: 0.8rem; letter-spacing: 0.03em; }
.badge-false { background: #7f1d1d; color: #fecaca !important; -webkit-text-fill-color: #fecaca; }
.badge-true { background: #14532d; color: #bbf7d0 !important; -webkit-text-fill-color: #bbf7d0; }
.badge-partial { background: #713f12; color: #fef08a !important; -webkit-text-fill-color: #fef08a; }

.myth-card { background: linear-gradient(135deg, #1e293b, #162032); border: 1px solid #334155; border-radius: 14px; padding: 1.5rem; margin: 1rem 0; }
.myth-card h4 { color: #f1f5f9 !important; -webkit-text-fill-color: #f1f5f9; font-weight: 600; margin: 0.5rem 0; font-size: 1.05rem; }
.myth-card p { color: #94a3b8 !important; -webkit-text-fill-color: #94a3b8; line-height: 1.7; }
.myth-card .myth-source { color: #64748b !important; -webkit-text-fill-color: #64748b; font-size: 0.8rem; margin-top: 0.75rem; }

button:focus-visible, input:focus-visible, select:focus-visible { outline: 3px solid #f59e0b !important; outline-offset: 2px; }
hr { border-color: #1e293b !important; }

.party-cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin: 1.5rem 0; }
.party-card { background: linear-gradient(145deg, #1e293b, #162032); border: 2px solid #334155; border-radius: 16px; padding: 1.5rem 1rem; text-align: center; cursor: pointer; transition: all 0.3s ease; position: relative; overflow: hidden; }
.party-card:hover { transform: translateY(-4px); box-shadow: 0 12px 32px rgba(0,0,0,0.3); }
.party-card.selected { border-color: #f59e0b !important; box-shadow: 0 0 24px rgba(245,158,11,0.25); }
.party-card .party-symbol { font-size: 2.5rem; margin-bottom: 0.5rem; display: block; }
.party-card .party-name { font-size: 0.95rem; font-weight: 700; color: #f1f5f9 !important; -webkit-text-fill-color: #f1f5f9; display: block; margin-bottom: 4px; }
.party-card .party-candidate { font-size: 0.8rem; color: #94a3b8 !important; -webkit-text-fill-color: #94a3b8; }
.party-card .check-mark { position: absolute; top: 10px; right: 10px; width: 24px; height: 24px; border-radius: 50%; background: #f59e0b; color: #000; display: none; align-items: center; justify-content: center; font-weight: 900; font-size: 14px; }
.party-card.selected .check-mark { display: flex; }
.party-card.nota-card { border-style: dashed; }

.icon-card-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1rem; margin: 1.5rem 0; }
.icon-card { background: linear-gradient(145deg, #1e293b, #162032); border: 1px solid #334155; border-radius: 16px; padding: 1.5rem; text-align: center; transition: all 0.3s ease; }
.icon-card:hover { border-color: #38bdf8; transform: translateY(-2px); box-shadow: 0 8px 24px rgba(56,189,248,0.1); }
.icon-card .ic-icon { font-size: 2.5rem; margin-bottom: 0.75rem; display: block; }
.icon-card .ic-title { font-size: 1rem; font-weight: 700; color: #f1f5f9 !important; -webkit-text-fill-color: #f1f5f9; margin-bottom: 6px; }
.icon-card .ic-desc { font-size: 0.85rem; color: #94a3b8 !important; -webkit-text-fill-color: #94a3b8; line-height: 1.5; }

.process-flow { display: flex; flex-wrap: wrap; gap: 0; margin: 1.5rem 0; justify-content: center; }
.flow-step { display: flex; flex-direction: column; align-items: center; text-align: center; flex: 1; min-width: 120px; max-width: 180px; position: relative; padding: 0 0.5rem; }
.flow-step .flow-icon { width: 56px; height: 56px; border-radius: 50%; background: linear-gradient(135deg, #14b8a6, #0d9488); display: flex; align-items: center; justify-content: center; font-size: 1.5rem; margin-bottom: 0.5rem; box-shadow: 0 4px 16px rgba(20,184,166,0.25); }
.flow-step .flow-label { font-size: 0.8rem; font-weight: 600; color: #e2e8f0 !important; -webkit-text-fill-color: #e2e8f0; }
.flow-step .flow-sub { font-size: 0.7rem; color: #64748b !important; -webkit-text-fill-color: #64748b; margin-top: 2px; }
.flow-arrow { display: flex; align-items: center; justify-content: center; font-size: 1.2rem; color: #475569; padding-top: 0.5rem; min-width: 24px; }

.evm-machine { background: linear-gradient(145deg, #1a2332, #0f172a); border: 2px solid #334155; border-radius: 20px; padding: 2rem; text-align: center; max-width: 500px; margin: 1rem auto; box-shadow: 0 8px 32px rgba(0,0,0,0.3); }
.evm-title { font-size: 0.75rem; color: #64748b !important; -webkit-text-fill-color: #64748b; letter-spacing: 0.15em; text-transform: uppercase; margin-bottom: 1rem; }
.evm-screen { background: #0a1628; border: 1px solid #1e3a5f; border-radius: 12px; padding: 1.25rem; margin-bottom: 1rem; }
.evm-selected-name { font-size: 1.3rem; font-weight: 700; color: #fbbf24 !important; -webkit-text-fill-color: #fbbf24; }
.evm-beep { display: inline-flex; align-items: center; gap: 6px; background: #14532d; border-radius: 20px; padding: 6px 16px; font-size: 0.8rem; color: #bbf7d0 !important; -webkit-text-fill-color: #bbf7d0; font-weight: 600; }
</style>
"""
