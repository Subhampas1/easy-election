# 🗳️ Citizen Election Assistant

> **AI-powered, multilingual election guidance platform** for Indian voters — built with Streamlit and 6 Google Cloud services.

[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red.svg)](https://streamlit.io)
[![Tests](https://img.shields.io/badge/Tests-99%20passed-brightgreen.svg)](#test-coverage)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Deploy: Cloud Run](https://img.shields.io/badge/Deploy-Cloud%20Run-4285F4.svg)](#deployment)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Google Cloud Services](#google-cloud-services)
- [Features](#features)
- [Security](#security)
- [Accessibility](#accessibility)
- [Performance](#performance)
- [Test Coverage](#test-coverage)
- [Project Structure](#project-structure)
- [Setup & Installation](#setup--installation)
- [Deployment](#deployment)
- [Environment Variables](#environment-variables)
- [API Reference](#api-reference)
- [Contributing](#contributing)

---

## Overview

Citizen Election Assistant is a production-grade, multilingual platform that guides Indian voters through every step of the democratic process — from registration to VVPAT verification. It leverages **6 Google Cloud services** (Cloud Logging, Cloud Storage, Google Maps, Vertex AI / Gemini, BigQuery, and Cloud Run) to deliver intelligent, data-driven election assistance.

### Key Highlights

| Metric | Value |
|--------|-------|
| **Google Cloud Services** | 6 (Logging, Storage, Maps, Vertex AI, BigQuery, Cloud Run) |
| **Test Coverage** | 99 tests across 2 test files — validators, engine, services, security, a11y |
| **Languages Supported** | 8 (English, Hindi, Tamil, Telugu, Bengali, Marathi, Gujarati, Kannada) |
| **WCAG Compliance** | AA+ with skip-nav, ARIA landmarks, high-contrast mode, reduced motion |
| **Security Layers** | Rate limiting, CSRF protection, CSP headers, input sanitization |
| **Architecture** | 4-layer modular (UI → Logic → Services → Utils) with OOP base classes |

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Streamlit Frontend                    │
│  (app.py → src/ui/pages.py + src/ui/styles.py)         │
├─────────────────────────────────────────────────────────┤
│                    Business Logic                        │
│  (src/logic/election_engine.py + prompt_builder.py)     │
├─────────────────────────────────────────────────────────┤
│                  Google Cloud Services                   │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────┐  │
│  │ Cloud    │ │ Cloud    │ │ Google   │ │ Vertex AI │  │
│  │ Logging  │ │ Storage  │ │ Maps API │ │ (Gemini)  │  │
│  └──────────┘ └──────────┘ └──────────┘ └───────────┘  │
│  ┌──────────┐ ┌──────────────────────────────────────┐  │
│  │ BigQuery │ │ Abstract BaseCloudService (OOP)      │  │
│  └──────────┘ └──────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────┤
│                     Utilities                            │
│  validators.py │ translations.py │ security.py          │
│  accessibility.py │ performance.py                      │
└─────────────────────────────────────────────────────────┘
```

### Design Principles

- **Separation of Concerns**: UI, logic, services, and utilities are strictly isolated.
- **OOP with Abstract Base Classes**: All Google services inherit from `BaseCloudService` ensuring consistent interfaces.
- **Graceful Degradation**: Every external service has an in-memory or rule-based fallback.
- **Type Safety**: Full type annotations across all modules.

---

## Google Cloud Services

### 1. Cloud Logging (`cloud_logging_service.py`)
- Structured JSON logging in production via `google-cloud-logging`.
- `log_user_action()` tracks all user interactions with structured metadata.
- Falls back to Python `logging` module locally.

### 2. Cloud Storage (`cloud_storage_service.py`)
- Serves election resources (voter guides, forms, FAQs) from GCS buckets.
- `list_available_resources()` returns downloadable documents.
- Falls back to a curated local resource list.

### 3. Google Maps Static API (`google_maps_service.py`)
- `get_polling_station_map_url()` renders a map centered on Delhi.
- `find_polling_stations()` returns nearest polling stations by PIN code.
- Falls back to OpenStreetMap embed when API key is unavailable.

### 4. Vertex AI / Gemini (`vertex_ai_service.py`)
- **AI Myth Verification**: `ai_verify_claim()` uses Gemini for intelligent fact-checking.
- **AI Voter Assistant**: `ai_answer_voter_query()` answers election questions with contextual knowledge.
- **Content Safety**: `ai_classify_content_safety()` screens user inputs for harmful content.
- Falls back to rule-based engine and keyword safety checks.

### 5. BigQuery (`bigquery_service.py`)
- **Event Tracking**: `track_event()` logs every user interaction for analytics.
- **Analytics Dashboard**: `get_analytics_summary()` aggregates event counts.
- **Feature Usage Reports**: `get_feature_usage_report()` tracks adoption metrics.
- **Regional Engagement**: `get_regional_engagement()` maps state-level participation.
- Falls back to in-memory `defaultdict` store.

### 6. Cloud Run (Deployment)
- Production container deployed on Google Cloud Run.
- `Dockerfile` with Python 3.11 slim base image.
- Health checks, auto-scaling, and HTTPS termination.

---

## Features

### 🗺️ Election Roadmap Generator
- Personalized voter registration checklist based on state and age.
- 8-step action plan for eligible voters, 3-step plan for underage users.
- State-specific helplines, websites, and regional notes.
- Required document checklist organized by category.

### 🗳️ EVM Ballot Simulator
- Interactive Electronic Voting Machine simulation with party cards.
- VVPAT (Voter Verifiable Paper Audit Trail) verification flow.
- Visual feedback with selection animations and confirmation.
- Educational EVM and VVPAT explanation expanders.

### 🔍 Myth Buster with AI Verification
- Database of 17+ curated election myths with verdicts and sources.
- Keyword-based search across the myth database.
- **AI-powered claim verification** using Google Gemini.
- Dual-mode: rule-based + AI verification side by side.

### 🤖 AI Election Assistant
- Natural language Q&A about Indian elections powered by Gemini.
- Contextual responses with ECI guideline citations.
- Party-neutral, accurate, and concise answers.

### 📍 Polling Station Finder
- PIN code-based polling station lookup.
- Google Maps Static API integration for visual maps.
- Distance and address information for each station.

### 📚 Election Resources
- Downloadable voter guides, forms, and FAQs from Cloud Storage.
- Categorized resource cards with descriptions and file sizes.

### 🌐 Multilingual Support
- 8 languages: English, Hindi, Tamil, Telugu, Bengali, Marathi, Gujarati, Kannada.
- Full UI translation including navigation, labels, and content.
- Language selector in sidebar with instant switching.

---

## Security

### Defense-in-Depth (`src/utils/security.py`)

| Feature | Implementation |
|---------|---------------|
| **Rate Limiting** | Token-bucket `RateLimiter` class — 30 req/min per session |
| **CSRF Protection** | `generate_csrf_token()` + `validate_csrf_token()` with constant-time comparison |
| **CSP Headers** | `generate_csp_header()` — strict Content Security Policy |
| **Session Fingerprinting** | SHA-256 fingerprint from User-Agent + Accept-Language |
| **Input Sanitization** | `sanitize_input()` strips HTML/script tags, enforces max length |
| **Input Validation** | `validate_input_length()` with field-specific constraints |
| **Content Safety** | AI-powered + keyword-based content classification |

### Input Validation (`src/utils/validators.py`)

- `sanitize_input()`: XSS prevention with HTML tag stripping.
- `validate_age()`: Range checking (1–120) with descriptive messages.
- `validate_state()`: Case-insensitive validation against official state list.
- `validate_zip_code()`: 6-digit Indian PIN code format validation.

---

## Accessibility

### WCAG 2.1 AA+ Compliance (`src/utils/accessibility.py`)

| Feature | Implementation |
|---------|---------------|
| **Skip Navigation** | Hidden skip-to-content link, visible on focus |
| **ARIA Landmarks** | `role="main"`, `role="navigation"`, `role="article"` |
| **Live Regions** | `aria-live="polite"` for dynamic content announcements |
| **High Contrast Mode** | Toggle in sidebar — inverts to high-contrast scheme |
| **Reduced Motion** | `prefers-reduced-motion` media query suppresses animations |
| **Focus Indicators** | `focus-visible` with 3px amber outline on all elements |
| **Screen Reader Only** | `.sr-only` utility class for hidden accessible text |
| **Contrast Checker** | `check_contrast_ratio()` — validates WCAG AA (4.5:1) and AAA (7:1) |
| **Accessible Forms** | `get_form_field_html()` with `aria-required`, `aria-describedby`, `aria-invalid` |
| **Semantic HTML** | Proper heading hierarchy, `role` attributes, `tabindex` |

---

## Performance

### Optimization Utilities (`src/utils/performance.py`)

| Feature | Implementation |
|---------|---------------|
| **TTL Caching** | `@timed_lru_cache` — LRU cache with time-based expiration |
| **Execution Timing** | `@measure_execution_time` — logs function duration in ms |
| **Lazy Loading** | `LazyLoader` class — defers expensive initialization |
| **Streamlit Cache** | `@st.cache_data` on static election data accessors |
| **Resource Monitoring** | `get_performance_metrics()` for health dashboards |

### Measured Performance

- **Page Load**: < 500ms (cached data paths)
- **API Fallback**: < 50ms (rule-based responses)
- **Test Suite**: 99 tests in ~1.7 seconds

---

## Test Coverage

### 99 Tests Across 2 Files

```
tests/test_app.py       — 54 tests (validators, engine, prompts, logging, static data)
tests/test_services.py  — 45 tests (security, performance, accessibility, AI, BigQuery)
```

| Module | Tests | Coverage Area |
|--------|-------|---------------|
| **Validators** | 16 | sanitize_input, validate_age, validate_state, validate_zip_code |
| **Election Engine** | 18 | generate_roadmap, simulate_ballot, check_myth, static data |
| **Prompt Builder** | 7 | roadmap, myth, ballot, eligibility prompts |
| **Cloud Logging** | 3 | Logger init, log_user_action |
| **Rate Limiter** | 4 | Allow, block, remaining, reset |
| **CSRF** | 4 | Generate, validate match/mismatch/empty |
| **CSP** | 1 | Header generation |
| **Session Security** | 5 | Fingerprint, input length, global rate limit |
| **Performance** | 5 | TTL cache, timing, lazy loader, metrics |
| **Accessibility** | 9 | Skip-nav, ARIA, live regions, forms, contrast |
| **Vertex AI** | 6 | Claim verify, query, safety, health, service name |
| **BigQuery** | 6 | Track event, summary, usage, regional, health |
| **Base Service** | 2 | Abstract enforcement, concrete instantiation |
| **Translations** | 4 | English, Hindi, missing key, lang code |

Run tests:
```bash
python -m pytest tests/ -v
```

---

## Project Structure

```
easy-election/
├── app.py                          # Entry point — page config, routing, security
├── Dockerfile                      # Cloud Run container (Python 3.11 slim)
├── requirements.txt                # Production dependencies
├── .env.example                    # Environment variable template
├── .gitignore                      # Git exclusions
├── .dockerignore                   # Docker exclusions
│
├── src/
│   ├── __init__.py
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── pages.py                # Page renderers (home, roadmap, ballot, myth)
│   │   └── styles.py               # CSS design system (glassmorphism)
│   ├── logic/
│   │   ├── __init__.py
│   │   ├── election_engine.py      # Core business logic + data models
│   │   └── prompt_builder.py       # Structured AI prompt templates
│   ├── services/
│   │   ├── __init__.py
│   │   ├── base_service.py         # Abstract BaseCloudService (OOP)
│   │   ├── cloud_logging_service.py # Google Cloud Logging
│   │   ├── cloud_storage_service.py # Google Cloud Storage
│   │   ├── google_maps_service.py   # Google Maps Static API
│   │   ├── vertex_ai_service.py     # Vertex AI / Gemini
│   │   └── bigquery_service.py      # Google BigQuery
│   └── utils/
│       ├── __init__.py
│       ├── validators.py           # Input sanitization + validation
│       ├── translations.py         # i18n (8 languages)
│       ├── security.py             # Rate limiting, CSRF, CSP
│       ├── accessibility.py        # WCAG 2.1 AA+ utilities
│       └── performance.py          # Caching, timing, lazy loading
│
└── tests/
    ├── __init__.py
    ├── test_app.py                 # 54 tests — core logic
    └── test_services.py            # 45 tests — services + utils
```

---

## Setup & Installation

### Prerequisites
- Python 3.11+
- Google Cloud project with APIs enabled

### Local Development

```bash
# Clone
git clone https://github.com/Subhampas1/easy-election.git
cd easy-election

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Run locally
streamlit run app.py

# Run tests
python -m pytest tests/ -v
```

---

## Deployment

### Google Cloud Run

```bash
# Build and deploy
gcloud run deploy easy-election \
  --source . \
  --region asia-south1 \
  --allow-unauthenticated \
  --set-env-vars GCP_PROJECT_ID=your-project-id
```

### Dockerfile

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8080
CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]
```

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GCP_PROJECT_ID` | Yes | Google Cloud project ID |
| `GOOGLE_CLOUD_LOGGING` | No | Enable Cloud Logging (`true`/`false`) |
| `GCS_BUCKET_NAME` | No | Cloud Storage bucket for resources |
| `GOOGLE_MAPS_API_KEY` | No | Google Maps Static API key |
| `GOOGLE_AI_API_KEY` | No | Vertex AI / Gemini API key |
| `BQ_DATASET_ID` | No | BigQuery dataset ID |
| `BQ_TABLE_ID` | No | BigQuery table ID |
| `APP_ENV` | No | `development` or `production` |
| `LOG_LEVEL` | No | Logging level (`DEBUG`, `INFO`, `WARNING`) |

---

## API Reference

### Services

| Function | Service | Description |
|----------|---------|-------------|
| `get_logger()` | Cloud Logging | Get structured logger instance |
| `log_user_action(action, details)` | Cloud Logging | Log user interaction |
| `list_available_resources()` | Cloud Storage | List election documents |
| `get_polling_station_map_url()` | Google Maps | Get static map URL |
| `find_polling_stations(pin)` | Google Maps | Find nearby stations |
| `ai_verify_claim(claim)` | Vertex AI | AI fact-checking |
| `ai_answer_voter_query(query)` | Vertex AI | AI Q&A |
| `ai_classify_content_safety(text)` | Vertex AI | Content moderation |
| `track_event(name, props)` | BigQuery | Track analytics event |
| `get_analytics_summary()` | BigQuery | Aggregated metrics |
| `get_feature_usage_report()` | BigQuery | Feature adoption data |
| `get_regional_engagement()` | BigQuery | State-level engagement |

### Utilities

| Function | Module | Description |
|----------|--------|-------------|
| `sanitize_input(text)` | validators | XSS prevention |
| `validate_age(age)` | validators | Age range validation |
| `t(key, lang)` | translations | i18n translation lookup |
| `check_rate_limit(session)` | security | Rate limit check |
| `generate_csrf_token()` | security | CSRF token generation |
| `generate_csp_header()` | security | CSP header string |
| `check_contrast_ratio(fg, bg)` | accessibility | WCAG contrast check |
| `timed_lru_cache(max, ttl)` | performance | TTL cache decorator |

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Run the test suite (`python -m pytest tests/ -v`)
4. Commit changes (`git commit -m "Add feature"`)
5. Push and open a Pull Request

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

<p align="center">
  Built with ❤️ for Indian Democracy<br>
  <strong>Citizen Election Assistant</strong> — Every Vote Counts 🇮🇳
</p>