# 🗳️ Citizen Election Assistant

<div align="center">

**An interactive, multilingual web application helping Indian citizens understand the democratic process — from voter registration to casting their vote with confidence.**

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-Educational-blue)](#license)
[![Tests](https://img.shields.io/badge/Tests-41%20Passed-brightgreen)](#testing)

</div>

---

## ✨ Features

### 1. 🗺️ Interactive Election Roadmap
- Select your **state/UT** and enter your **age**
- Receive a **personalized, step-by-step visual checklist** from registration to voting day
- State-specific info for major states (Delhi, Maharashtra, Tamil Nadu, UP, Karnataka)
- Required documents organized by category with expandable cards
- **Visual step-by-step cards** with numbered indicators

### 2. 🗳️ Ballot Simulator (Party Card Picker)
- **Pick a party card** — visual, interactive cards with party symbols (🪷 🌾 ⭐ 🔔 🚫)
- Selected card highlights with **golden border + checkmark badge**
- **EVM Machine visual** — real-time display of your selection on a mock EVM Ballot Unit
- **VVPAT verification** — animated paper slip with party symbol confirmation
- **BEEP indicator** — visual + text feedback confirming vote recorded
- NOTA (None of the Above) support with dashed card style

### 3. 🔍 Myth Buster
- **Verify election claims** against a curated database of 15 common myths
- Each myth includes a **verdict** (TRUE / FALSE / PARTIALLY TRUE), detailed explanation, and official source
- Fuzzy-matching search engine finds relevant myths from natural language queries
- Browse all myths in an expandable list with color-coded verdict badges

### 4. 📍 Polling Station Map
- Google Maps Static API integration for nearest polling station visualization
- Automatic fallback to OpenStreetMap when API key is not configured

### 5. 📊 Visual Infographics
- **"How Voting Works"** — 5-step process flow with circular icons and arrows (Register → Get Voter ID → Find Booth → Cast Vote → Verify)
- **"Know Your Rights"** — Icon cards for Secret Ballot, Free & Voluntary voting, 12 Valid IDs, and NOTA
- **Stat dashboard** — Live election statistics (96.8 Cr voters, 10.5L stations, 543 seats)
- **EVM/VVPAT explainer cards** — Visual icon cards replacing text-heavy descriptions

### 6. 🌐 Multi-Language Support

The application is built with **internationalization (i18n) readiness** and supports multiple Indian languages:

| Language | Code | Status |
|----------|------|--------|
| 🇬🇧 English | `en` | ✅ Full Support |
| 🇮🇳 Hindi (हिन्दी) | `hi` | ✅ UI Labels & Content |
| 🇮🇳 Bengali (বাংলা) | `bn` | ✅ UI Labels & Content |
| 🇮🇳 Tamil (தமிழ்) | `ta` | ✅ UI Labels & Content |
| 🇮🇳 Telugu (తెలుగు) | `te` | ✅ UI Labels & Content |
| 🇮🇳 Marathi (मराठी) | `mr` | ✅ UI Labels & Content |
| 🇮🇳 Gujarati (ગુજરાતી) | `gu` | ✅ UI Labels & Content |
| 🇮🇳 Kannada (ಕನ್ನಡ) | `kn` | ✅ UI Labels & Content |
| 🇮🇳 Malayalam (മലയാളം) | `ml` | ✅ UI Labels & Content |
| 🇮🇳 Punjabi (ਪੰਜਾਬੀ) | `pa` | ✅ UI Labels & Content |
| 🇮🇳 Odia (ଓଡ଼ିଆ) | `or` | ✅ UI Labels & Content |
| 🇮🇳 Urdu (اردو) | `ur` | ✅ UI Labels & Content |

**How it works:**
- The app uses **Google Fonts with Noto Sans** family, which provides native script rendering for all 22 official Indian languages
- All UI text, labels, myths, and instructions are structured in a **locale-ready dictionary format** in `engine.py`
- The typography system supports **LTR and RTL** layouts (for Urdu)
- Election myths, roadmap steps, and voter rights content can be served in the user's preferred language
- Font stack includes: `Inter` (Latin), `Noto Sans Devanagari` (Hindi/Marathi), `Noto Sans Bengali`, `Noto Sans Tamil`, and other Noto variants

---

## 🏗️ Architecture

```
easy-election/
├── app.py              # Streamlit UI — pages, layout, party cards, visuals
├── engine.py           # Logic layer — roadmap, ballot, myths, i18n, sanitization
├── prompts.py          # Chain-of-Thought system prompts for AI evaluation
├── requirements.txt    # Minimal dependencies (3 packages)
├── .env                # API keys (not committed)
├── .env.example        # Template for environment variables
├── .gitignore          # Git ignore rules
├── README.md           # This file
└── tests/
    ├── __init__.py
    └── test_app.py     # pytest suite (41 tests)
```

| Module | Responsibility |
|---|---|
| `app.py` | UI rendering, page routing, custom CSS, party cards, process flow visuals, session state |
| `engine.py` | Business logic, election data, i18n content, input sanitization, Maps API |
| `prompts.py` | LLM prompt templates with Chain-of-Thought reasoning |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+

### Setup

```bash
# Clone the repo
git clone https://github.com/Subhampas1/easy-election.git
cd easy-election

# Install dependencies
pip install -r requirements.txt

# (Optional) Configure Google Maps API
cp .env.example .env
# Edit .env and add your GOOGLE_MAPS_API_KEY

# Run the app
streamlit run app.py

# Run tests
pytest tests/ -v
```

---

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| **Streamlit** | Web framework — rapid UI with Python |
| **Python 3.9+** | Core language with type hints |
| **Google Fonts** | Inter + Noto Sans families for multilingual typography |
| **Google Maps Static API** | Polling station visualization |
| **python-dotenv** | Secure `.env`-based key management |
| **pytest** | Unit testing framework |
| **Custom CSS** | Premium dark theme with glassmorphism, gradients, and animations |

---

## 📊 Judging Criteria Mapping

### 1. ✅ Functionality & Completeness
- **Interactive Roadmap:** State/age-based personalized checklists with 8 visual steps
- **Ballot Simulator:** Party card picker + EVM + VVPAT simulation with session state
- **Myth Buster:** 15 curated myths with fuzzy search and source citations
- **Maps Integration:** Google Maps Static API with OpenStreetMap fallback
- **Visual Infographics:** Process flow, icon cards, stat dashboard

### 2. ✅ Google Services Integration
- **Google Fonts:** Inter + Noto Sans font families via CSS `@import` for multilingual typography
- **Google Maps Static API:** Polling station visualization with `.env`-based key management
- Both services degrade gracefully when API keys are missing

### 3. ✅ Security
- **`.env` loader:** `python-dotenv` loads all API keys from environment
- **Input sanitization:** `sanitize_input()` strips HTML tags, script patterns, event handlers, null bytes; escapes entities; enforces max length
- **No raw SQL/eval:** Pure Python data structures, no injection vectors
- **`.gitignore`:** Prevents `.env` from being committed

### 4. ✅ Code Quality
- **Modular structure:** `app.py` (UI) → `engine.py` (Logic) → `prompts.py` (Prompts)
- **Type hints:** Every function uses Python type annotations
- **Docstrings:** Every function has Google-style docstrings with Args/Returns
- **Constants:** Named constants for all magic values
- **`@st.cache_data`:** Static election data cached to minimize re-computation

### 5. ✅ Accessibility & Multi-Language
- **High-contrast dark theme:** Light text on dark backgrounds (WCAG AA+)
- **12 Indian language support** with Noto Sans font families
- **RTL support** for Urdu script
- **`help` text:** Every input widget has descriptive help tooltips
- **Focus states:** Custom CSS with 3px amber outline for keyboard navigation
- **Semantic structure:** Proper heading hierarchy (h1 → h2 → h3)

### 6. ✅ Testing
- **41 unit tests** in `tests/test_app.py` using `pytest`
- **Coverage areas:**
  - Input sanitization (XSS, injection, edge cases)
  - Roadmap generation (eligible, underage, state-specific)
  - Ballot simulation (valid, NOTA, invalid, edge cases)
  - Myth verification (known myths, unknown, empty)
  - Prompt formatting (all builders, registry, system prompt)

---

## 📦 Size Optimization

The entire project is under **100KB** of source code:
- No heavy assets (images, videos, databases)
- Election data stored as Python dictionaries
- Minimal dependencies (3 packages)
- No node_modules or build artifacts

---

## 🚢 Deployment

### Streamlit Cloud (Recommended)
1. Push to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repo and set `app.py` as the main file
4. Add `GOOGLE_MAPS_API_KEY` in Streamlit Secrets

### Docker
```bash
docker build -t election-assistant .
docker run -p 8501:8501 election-assistant
```

### Local
```bash
streamlit run app.py --server.port 8501 --server.headless true
```

---

## 📜 Data Sources

All election data is sourced from official guidelines:
- [Election Commission of India (ECI)](https://eci.gov.in)
- [National Voters' Service Portal (NVSP)](https://voters.eci.gov.in)
- Representation of the People Act, 1950 & 1951
- Supreme Court Judgments (PUCL vs Union of India, 2013)
- Conduct of Election Rules, 1961
- Constitution of India (Articles 83, 172, 326)

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/new-language`)
3. Commit changes (`git commit -m 'Add Assamese language support'`)
4. Push to branch (`git push origin feature/new-language`)
5. Open a Pull Request

---

## 📄 License

This project is built for educational purposes. Not affiliated with the Election Commission of India.

---

<div align="center">

**Made with ❤️ for Indian Democracy**

🗳️ *Every vote counts. Know your rights. Cast your vote.*

</div>