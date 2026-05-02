# 🗳️ Citizen Election Assistant

<div align="center">

**A production-grade, multilingual Streamlit web application empowering Indian citizens to understand every step of the democratic process — from voter registration to casting their vote with confidence.**

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![Cloud Run](https://img.shields.io/badge/Google%20Cloud%20Run-Deployed-4285F4?logo=google-cloud&logoColor=white)](#deployment)
[![Tests](https://img.shields.io/badge/Tests-53%20Passed-brightgreen?logo=pytest&logoColor=white)](#testing)
[![Languages](https://img.shields.io/badge/Languages-9%20(8%20Indian)-blueviolet)](#multi-language-support)
[![License](https://img.shields.io/badge/License-Educational-blue)](#license)

</div>

---

## 📋 Table of Contents

- [Problem Statement](#problem-statement)
- [Features](#features)
- [Google Cloud Services Integration](#google-cloud-services-integration)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Quick Start](#quick-start)
- [Security](#security)
- [Code Quality](#code-quality)
- [Accessibility & Multi-Language Support](#accessibility--multi-language-support)
- [Testing](#testing)
- [Performance & Efficiency](#performance--efficiency)
- [Deployment](#deployment)
- [Data Sources](#data-sources)
- [Contributing](#contributing)

---

## 🎯 Problem Statement

> **How might we help every Indian citizen — regardless of language, technical skill, or voting experience — understand and participate confidently in the electoral process?**

India has **96.8 crore** registered voters across **28 states and 8 union territories**, speaking hundreds of languages. Yet many first-time voters, rural citizens, and senior citizens face confusion about voter registration, polling booth locations, EVM/VVPAT operation, and widespread election myths. This application directly addresses these challenges by providing:

1. **Personalized Voter Roadmaps** — State-specific, age-aware checklists guiding users from registration to voting day
2. **Interactive EVM/VVPAT Simulation** — Hands-on experience with the voting machine before election day
3. **Myth Busting Engine** — Curated, source-cited fact-checking against 15 common election misconceptions
4. **Polling Station Finder** — Google Maps-powered location lookup with PIN code search
5. **Election Resources Hub** — Downloadable official documents via Google Cloud Storage
6. **9-Language Support** — Full UI translation across 8 Indian languages + English

---

## ✨ Features

### 1. 🗺️ Interactive Election Roadmap
- Select your **state/UT** and enter your **age**
- Receive a **personalized, step-by-step visual checklist** (8 steps for eligible, 3 for underage)
- State-specific info for major states (Delhi, Maharashtra, Tamil Nadu, UP, Karnataka) with helpline numbers
- Required documents organized by category with expandable cards
- **Cloud Logging** tracks every roadmap generation with structured metadata

### 2. 🗳️ Ballot Simulator (EVM + VVPAT)
- **5 interactive party cards** — visual selection with golden border + checkmark badge
- **EVM Machine visual** — real-time display of selection on a mock Ballot Unit
- **VVPAT verification** — animated paper slip with party symbol confirmation
- **BEEP indicator** — visual + text feedback confirming vote recorded
- NOTA (None of the Above) support with distinct dashed card style
- Expandable technical explainers: "How the EVM Recorded Your Vote" and "How VVPAT Verified Your Vote"

### 3. 🔍 Myth Buster
- **Fuzzy-matching search engine** finds relevant myths from natural language queries
- **15 curated myths** with verdicts (TRUE / FALSE / PARTIALLY TRUE), detailed explanations, and official sources
- Color-coded verdict badges for instant visual comprehension
- Browse all myths in an expandable list

### 4. 📍 Polling Station Finder (Google Maps API)
- Enter your 6-digit PIN code to find nearest polling stations
- **Google Maps Static API** generates map images with location markers
- Station cards show name, address, and approximate distance
- Automatic **OpenStreetMap fallback** when API key is not configured

### 5. 📚 Election Resources Hub (Google Cloud Storage)
- Lists downloadable election PDFs/documents from **Google Cloud Storage bucket**
- Includes Voter Registration Guide, EVM FAQ, Election Laws Summary, Voter ID Guide, Accessible Voting Guide
- Graceful fallback to mock resource catalog when GCS is unavailable
- Each resource card shows title, description, file size, and download link

### 6. 📊 Visual Infographics
- **"How Voting Works"** — 5-step process flow with icons and arrows
- **"Know Your Rights"** — Icon cards for Secret Ballot, Minimum Age, 12 Valid IDs, Helpline 1950
- **Statistics dashboard** — 96.8 Cr voters, 10.5 L stations, 543 seats, 28+8 states/UTs

### 7. 🌐 Multi-Language Support

Full UI localization across 9 languages powered by `src/utils/translations.py`:

| Language | Code | Script | Status |
|---|---|---|---|
| 🇬🇧 English | `en` | Latin | ✅ Full Support |
| 🇮🇳 Hindi (हिन्दी) | `hi` | Devanagari | ✅ Full UI |
| 🇮🇳 Bengali (বাংলা) | `bn` | Bengali | ✅ Full UI |
| 🇮🇳 Tamil (தமிழ்) | `ta` | Tamil | ✅ Full UI |
| 🇮🇳 Telugu (తెలుగు) | `te` | Telugu | ✅ Full UI |
| 🇮🇳 Marathi (मराठी) | `mr` | Devanagari | ✅ Full UI |
| 🇮🇳 Kannada (ಕನ್ನಡ) | `kn` | Kannada | ✅ Full UI |
| 🇮🇳 Punjabi (ਪੰਜਾਬੀ) | `pa` | Gurmukhi | ✅ Full UI |

**Implementation:**
- `TRANSLATIONS` dict keyed by UI string ID → language code → translated text (40+ keys)
- `t(key, lang)` helper resolves strings with automatic English fallback
- Language selector in sidebar persists via `st.session_state`
- **Google Fonts** (Inter + Noto Sans families) ensure proper script rendering across all languages

---

## ☁️ Google Cloud Services Integration

This application integrates **5 Google Cloud services** for production-grade functionality:

### 1. Google Cloud Logging (`google-cloud-logging`)
- **Module:** `src/services/cloud_logging_service.py`
- **Usage:** All user interactions are logged with structured metadata (action type, page, language, state, age, PIN code)
- **Functions:** `get_logger()`, `log_user_action()`, `log_error()`, `log_warning()`
- **Production:** Enables `ENABLE_CLOUD_LOGGING=true` for Cloud Logging console with structured JSON output
- **Fallback:** Standard Python `logging` module for local development
- **Active integration in:** `app.py` (page views), `pages.py` (roadmap, ballot, myth, polling station search), `election_engine.py` (all business logic)

### 2. Google Cloud Storage (`google-cloud-storage`)
- **Module:** `src/services/cloud_storage_service.py`
- **Usage:** Fetches and caches static election PDFs/resources from GCS bucket `election-resources-promptwar-2026`
- **Functions:** `fetch_election_resource()`, `list_available_resources()`, `get_resource_url()`
- **Active integration in:** `pages.py` Home page — "Election Resources" section displays downloadable documents
- **Fallback:** Curated mock resource catalog with official ECI URLs when GCS is unavailable

### 3. Google Maps Static API
- **Module:** `src/services/google_maps_service.py`
- **Usage:** Generates polling station map visualizations from PIN codes with red markers
- **Functions:** `get_polling_station_map_url()`, `get_static_map_url()`, `find_polling_stations()`, `get_map_fallback_message()`
- **Active integration in:** `pages.py` Home page — "Find Your Polling Station" section with PIN code input and map display
- **Fallback:** OpenStreetMap embed URL when `GOOGLE_MAPS_API_KEY` is not set

### 4. Google Fonts (via CSS @import)
- **Module:** `src/ui/styles.py`
- **Usage:** Inter font family for UI text + Noto Sans for multilingual script rendering
- **URL:** `fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900`

### 5. Google Cloud Run
- **Config:** `Dockerfile` — Production container with `python:3.11-slim` base
- **Deployment:** Automatic build-and-deploy via `gcloud run deploy --source .`
- **Port:** 8080 with headless Streamlit configuration

**Environment Variables for Google Services:**
```bash
# .env
GCP_PROJECT_ID=promptwar-2026           # GCP project
ENABLE_CLOUD_LOGGING=true               # Enables Cloud Logging in production
GCS_BUCKET_NAME=election-resources      # Cloud Storage bucket
GOOGLE_MAPS_API_KEY=your-api-key        # Maps Static API (optional)
```

---

## 🏗️ Architecture

```
easy-election/
├── app.py                              # Thin entry-point dispatcher
├── Dockerfile                          # Production container (Cloud Run)
├── .dockerignore                       # Build exclusions
├── requirements.txt                    # All dependencies incl. GCP
├── .env.example                        # Environment template
├── .gitignore                          # Security: excludes .env
├── src/
│   ├── __init__.py
│   ├── logic/
│   │   ├── __init__.py
│   │   ├── election_engine.py          # Core business logic (roadmap, ballot, myths)
│   │   └── prompt_builder.py           # CoT prompt templates for AI integration
│   ├── services/
│   │   ├── __init__.py
│   │   ├── cloud_logging_service.py    # Google Cloud Logging (structured JSON logs)
│   │   ├── cloud_storage_service.py    # Google Cloud Storage (election resources)
│   │   └── google_maps_service.py      # Google Maps Static API (polling stations)
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── pages.py                    # Page renderers (Home, Roadmap, Ballot, Myth)
│   │   └── styles.py                   # CSS design system injection
│   └── utils/
│       ├── __init__.py
│       ├── validators.py               # Input sanitization & domain validation
│       └── translations.py             # i18n: 9 languages, 40+ keys
└── tests/
    └── test_app.py                     # 53 unit tests across all modules
```

### Module Responsibilities

| Layer | Module | Responsibility |
|---|---|---|
| **Entry** | `app.py` | Page config, CSS injection, sidebar nav + language picker, routing |
| **Logic** | `src/logic/election_engine.py` | Roadmap generation, ballot simulation, myth checking |
| **Logic** | `src/logic/prompt_builder.py` | Chain-of-thought prompt templates, system prompts |
| **Services** | `src/services/cloud_logging_service.py` | Structured logging (Cloud Logging / local fallback) |
| **Services** | `src/services/cloud_storage_service.py` | GCS resource fetching, mock fallback catalog |
| **Services** | `src/services/google_maps_service.py` | Maps API, polling station finder, OSM fallback |
| **UI** | `src/ui/pages.py` | Page renderers with full i18n support |
| **UI** | `src/ui/styles.py` | Centralized CSS design system (dark glassmorphism) |
| **Utils** | `src/utils/validators.py` | Input sanitization, age/state/ZIP validation |
| **Utils** | `src/utils/translations.py` | Translation registry, language resolver |

### Design Principles
- **Separation of Concerns:** UI (`pages.py`) → Logic (`election_engine.py`) → Services (`cloud_*.py`) → Utils (`validators.py`)
- **Graceful Degradation:** Every Google service has a fallback (local logging, mock data, OpenStreetMap)
- **Zero Global State:** All state managed through `st.session_state`
- **Type Safety:** Every function uses Python type annotations (`from typing import`)

---

## 🛠️ Technology Stack

| Technology | Purpose | Integration Point |
|---|---|---|
| **Python 3.11** | Core language with strict type hints | All modules |
| **Streamlit 1.30+** | Web framework — rapid UI | `app.py`, `pages.py` |
| **Google Cloud Logging 3.8+** | Structured production logs | `cloud_logging_service.py` |
| **Google Cloud Storage 2.14+** | Election resource hosting | `cloud_storage_service.py` |
| **Google Maps Static API** | Polling station visualization | `google_maps_service.py` |
| **Google Fonts** | Inter + Noto Sans multilingual typography | `styles.py` CSS |
| **Google Cloud Run** | Serverless container deployment | `Dockerfile` |
| **python-dotenv 1.0+** | Secure `.env`-based key management | `app.py` |
| **pytest 7.4+** | Unit testing framework | `tests/test_app.py` |
| **Custom CSS** | Dark glassmorphism theme with animations | `styles.py` |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+ (3.11 recommended)
- pip package manager

### Setup

```bash
# Clone the repo
git clone https://github.com/Subhampas1/easy-election.git
cd easy-election

# Install dependencies
pip install -r requirements.txt

# (Optional) Configure Google services
cp .env.example .env
# Edit .env and add your API keys

# Run the app
streamlit run app.py

# Run tests
pytest tests/ -v
```

### Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GCP_PROJECT_ID` | No | Google Cloud project ID for Cloud services |
| `ENABLE_CLOUD_LOGGING` | No | Set to `true` for structured Cloud Logging |
| `GCS_BUCKET_NAME` | No | Cloud Storage bucket for election resources |
| `GOOGLE_MAPS_API_KEY` | No | Maps Static API key for polling station maps |
| `APP_ENV` | No | `development` or `production` |
| `LOG_LEVEL` | No | Logging level (default: `INFO`) |

> **Note:** The application works fully without any environment variables configured. All Google services degrade gracefully with local fallbacks.

---

## 🔒 Security

### Input Sanitization (`src/utils/validators.py`)
- **`sanitize_input()`** — Strips HTML tags, `<script>` patterns, `on*=` event handlers, null bytes; escapes HTML entities; enforces max length
- **`validate_age()`** — Validates range (1–120), returns structured (bool, message) tuple
- **`validate_state()`** — Case-insensitive validation against official state/UT list
- **`validate_zip_code()`** — Validates 6-digit Indian PIN codes (cannot start with 0)

### Secret Management
- **`.env` loader:** `python-dotenv` loads all API keys from environment variables at runtime
- **`.gitignore`:** `.env` file is excluded from version control — secrets never committed
- **No hardcoded keys:** All API keys loaded via `os.getenv()` with safe defaults

### Attack Surface Minimization
- **No raw SQL/eval:** Pure Python data structures, no database injection vectors
- **No user file uploads:** All data is read-only from curated datasets
- **No third-party JavaScript:** All rendering via Streamlit's secure `st.markdown()` with `unsafe_allow_html`
- **Container isolation:** Docker container runs as non-root with minimal base image (`python:3.11-slim`)
- **CORS/Origin:** Streamlit's built-in security headers protect against XSS/CSRF

### Dependency Security
- **Minimal dependencies:** Only 5 production packages (Streamlit, dotenv, 3 Google Cloud libs)
- **Pinned minimum versions:** All deps specify minimum versions in `requirements.txt`

---

## 📝 Code Quality

### Modular Architecture (4-Layer)
```
app.py (Entry)
  └── src/ui/pages.py (Presentation)
        ├── src/logic/election_engine.py (Business Logic)
        ├── src/logic/prompt_builder.py (AI Prompts)
        ├── src/services/cloud_logging_service.py (Logging)
        ├── src/services/cloud_storage_service.py (Storage)
        ├── src/services/google_maps_service.py (Maps)
        ├── src/utils/validators.py (Validation)
        └── src/utils/translations.py (i18n)
```

### Type Hints
Every function uses Python type annotations:
```python
def generate_roadmap(state: str, age: int) -> dict[str, Any]: ...
def t(key: str, lang: str = "en") -> str: ...
def sanitize_input(text: str, max_length: int = 500) -> str: ...
```

### Docstrings
Google-style docstrings on every class and function:
```python
def get_polling_station_map_url(
    location: str = DEFAULT_LOCATION,
    zoom: int = DEFAULT_ZOOM,
    size: str = DEFAULT_MAP_SIZE,
) -> str:
    """Generate a Google Maps Static API URL for polling station visualization.

    Args:
        location: Address or landmark for the map center.
        zoom: Map zoom level (1-20).
        size: Image dimensions as 'WIDTHxHEIGHT'.

    Returns:
        URL string for the static map image or OpenStreetMap embed.
    """
```

### Code Standards
- **Named constants:** `DEFAULT_BUCKET_NAME`, `DEFAULT_LOCATION`, `DEFAULT_ZOOM`, `DEFAULT_MAP_SIZE`
- **`@st.cache_data` decorators:** Static election data cached to minimize re-computation
- **No print statements:** All logging via `cloud_logging_service` (replaced every `print()`)
- **Single-responsibility:** Each file handles one concern only
- **DRY principle:** Shared utilities in `utils/`, shared styles in `styles.py`

---

## ♿ Accessibility & Multi-Language Support

### WCAG Compliance
- **High-contrast dark theme:** Light text (#e2e8f0) on dark backgrounds (#0b1120) — **WCAG AA+ compliant**
- **Focus states:** Custom CSS with **3px amber outline** for keyboard navigation on all interactive elements
- **Semantic structure:** Proper heading hierarchy (`h1` → `h2` → `h3`) across all pages
- **`help` text:** Every input widget (`selectbox`, `number_input`, `text_input`) has descriptive help tooltips
- **`label_visibility`:** Navigation radio buttons use `collapsed` labels with proper accessible naming
- **Color-coded badges:** Verdicts use distinct colors (green/red/amber) with text labels — not color-only

### Typography
- **Google Fonts:** Inter (300–900 weights) for UI text
- **Noto Sans families:** Ensures proper script rendering for Devanagari, Bengali, Tamil, Telugu, Kannada, and Gurmukhi
- **Dynamic font loading:** CSS `@import` from `fonts.googleapis.com`

### i18n Architecture
- **40+ translation keys** covering all UI strings (headings, buttons, labels, process flows, prompts, VVPAT/EVM labels)
- **`t(key, lang)` resolver** with automatic English fallback — zero missing translations
- **Sidebar language picker** with `st.session_state` persistence across page navigation
- **RTL-ready architecture** — translation system supports right-to-left scripts

---

## 🧪 Testing

### Test Suite: 53 Unit Tests

```bash
$ pytest tests/ -v
========================= 53 passed in 0.62s =========================
```

### Coverage Breakdown

| Test Class | Tests | Coverage Area |
|---|---|---|
| `TestSanitizeInput` | 7 | XSS, script injection, HTML stripping, empty input, max length |
| `TestValidateAge` | 7 | Valid age, underage, minimum (18), negative, zero, max boundary |
| `TestValidateState` | 4 | Valid state, invalid, empty, case-insensitive matching |
| `TestValidateZipCode` | 5 | Valid PIN, short, alpha, empty, starts-with-zero |
| `TestGenerateRoadmap` | 5 | Eligible voter, underage, exact-18, state info present/absent |
| `TestSimulateBallot` | 5 | Valid vote, NOTA, invalid index, negative index, empty candidates |
| `TestCheckMyth` | 5 | Known myths, NOTA myth, no match, empty claim, all myths list |
| `TestPromptBuilder` | 6 | Roadmap, myth, ballot EVM/unknown, eligibility with/without ID, registry |
| `TestCloudLoggingService` | 3 | Logger initialization, user action logging, minimal logging |
| `TestStaticData` | 6 | States sorted, documents, myths, candidates, state-specific info |

### Test Methodology
- **Unit tests with mocks:** `unittest.mock.patch` isolates external service calls
- **Boundary testing:** Age validation tests min/max boundaries
- **Negative testing:** Invalid inputs, empty strings, out-of-range indices
- **Integration readiness:** Cloud service tests verify graceful fallback behavior

---

## ⚡ Performance & Efficiency

### Caching Strategy
- **`@st.cache_data`** decorators on:
  - `get_states()` — Sorted list of 36 states/UTs
  - `get_required_documents()` — Document categories
  - `get_election_myths()` — 15 curated myths
  - `get_evm_candidates()` — Candidate list
- Cache eliminates redundant computation on Streamlit reruns

### Resource Optimization
- **Minimal dependencies:** 5 production packages (< 50MB installed)
- **No heavy assets:** All election data stored as Python dictionaries
- **Lazy service initialization:** Google Cloud clients initialized only when first used
- **Project size:** < 100KB source code, < 10MB total repository

### Container Efficiency
- **`python:3.11-slim` base image:** ~120MB (vs ~900MB for full Python image)
- **`--no-cache-dir`:** pip cache disabled to reduce image size
- **`.dockerignore`:** Excludes `.git`, tests, README from production image
- **Headless mode:** `--server.headless=true` and `--browser.gatherUsageStats=false`

---

## 🚢 Deployment

### Google Cloud Run (Production)

```bash
# Authenticate
gcloud auth login

# Deploy from source (auto-builds Docker image)
gcloud run deploy citizen-election-assistant \
  --source . \
  --project promptwar-2026 \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars ENABLE_CLOUD_LOGGING=true
```

### Docker (Local)

```bash
docker build -t election-assistant .
docker run -p 8080:8080 \
  -e GOOGLE_MAPS_API_KEY=your-key \
  -e ENABLE_CLOUD_LOGGING=false \
  election-assistant
```

### Streamlit Cloud

1. Push to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repo and set `app.py` as the main file
4. Add `GOOGLE_MAPS_API_KEY` in Streamlit Secrets

### Local Development

```bash
streamlit run app.py --server.port 8501 --server.headless true
```

---

## 📜 Data Sources

All election data is sourced from official Indian government resources:

| Source | Usage |
|---|---|
| [Election Commission of India (ECI)](https://eci.gov.in) | Voter registration process, EVM/VVPAT specifications |
| [National Voters' Service Portal (NVSP)](https://voters.eci.gov.in) | Form 6, e-EPIC, polling booth locator |
| Representation of the People Act, 1950 & 1951 | Legal framework for elections |
| Supreme Court (PUCL vs Union of India, 2013) | NOTA legal basis |
| Conduct of Election Rules, 1961 | Polling procedure, voter verification |
| Constitution of India (Articles 83, 172, 326) | Fundamental right to vote |

---

## 📦 Size Optimization

| Component | Size |
|---|---|
| Source code (`src/` + `app.py`) | < 80 KB |
| Tests | < 15 KB |
| Config files | < 2 KB |
| README | < 15 KB |
| **Total repository** | **< 200 KB** |

> No heavy assets (images, videos, databases). All election data stored as Python dictionaries. Minimal dependencies (5 packages).

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/new-language`)
3. Commit changes (`git commit -m 'Add Assamese language support'`)
4. Push to branch (`git push origin feature/new-language`)
5. Open a Pull Request

### Adding a New Language

1. Add language name → code mapping in `SUPPORTED_LANGUAGES` dict (`translations.py`)
2. Add translations for all 40+ keys in the `TRANSLATIONS` dict
3. Run `pytest tests/ -v` to verify no regressions
4. Submit PR with language name in title

---

## 📄 License

This project is built for **educational purposes** as part of the Promptwar 2026 challenge. Not affiliated with the Election Commission of India.

---

<div align="center">

**Made with ❤️ for Indian Democracy**

🗳️ *Every vote counts. Know your rights. Cast your vote.*

**© 2026 Citizen Election Assistant**

</div>