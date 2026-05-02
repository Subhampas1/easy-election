"""
test_services.py — Tests for Security, Performance, Accessibility,
Vertex AI, and BigQuery modules.
"""
import pytest
import time
from unittest.mock import patch, MagicMock

# ── Security Tests ───────────────────────────────────────────────
class TestRateLimiter:
    def test_allows_under_limit(self):
        from src.utils.security import RateLimiter
        rl = RateLimiter(window=60, max_requests=5)
        assert rl.is_allowed("u1") is True

    def test_blocks_over_limit(self):
        from src.utils.security import RateLimiter
        rl = RateLimiter(window=60, max_requests=2)
        rl.is_allowed("u2")
        rl.is_allowed("u2")
        assert rl.is_allowed("u2") is False

    def test_remaining(self):
        from src.utils.security import RateLimiter
        rl = RateLimiter(window=60, max_requests=5)
        rl.is_allowed("u3")
        assert rl.get_remaining("u3") == 4

    def test_reset(self):
        from src.utils.security import RateLimiter
        rl = RateLimiter(window=60, max_requests=2)
        rl.is_allowed("u4")
        rl.is_allowed("u4")
        rl.reset("u4")
        assert rl.is_allowed("u4") is True

class TestCSRF:
    def test_generate_token(self):
        from src.utils.security import generate_csrf_token
        t = generate_csrf_token()
        assert len(t) == 64

    def test_validate_matching(self):
        from src.utils.security import generate_csrf_token, validate_csrf_token
        t = generate_csrf_token()
        assert validate_csrf_token(t, t) is True

    def test_validate_mismatch(self):
        from src.utils.security import validate_csrf_token
        assert validate_csrf_token("a", "b") is False

    def test_validate_empty(self):
        from src.utils.security import validate_csrf_token
        assert validate_csrf_token("", "x") is False

class TestCSP:
    def test_csp_header(self):
        from src.utils.security import generate_csp_header
        csp = generate_csp_header()
        assert "default-src" in csp
        assert "script-src" in csp

class TestSessionSecurity:
    def test_fingerprint(self):
        from src.utils.security import generate_session_fingerprint
        fp = generate_session_fingerprint("Mozilla/5.0", "en-US")
        assert len(fp) == 64

    def test_input_length_valid(self):
        from src.utils.security import validate_input_length
        ok, msg = validate_input_length("hello", 500)
        assert ok is True

    def test_input_length_exceeded(self):
        from src.utils.security import validate_input_length
        ok, msg = validate_input_length("x" * 600, 500)
        assert ok is False

    def test_input_non_string(self):
        from src.utils.security import validate_input_length
        ok, msg = validate_input_length(123, 500)
        assert ok is False

    def test_global_rate_limit(self):
        from src.utils.security import check_rate_limit
        assert check_rate_limit("test_session") is True

# ── Performance Tests ────────────────────────────────────────────
class TestTimedLruCache:
    def test_caching(self):
        from src.utils.performance import timed_lru_cache
        call_count = 0
        @timed_lru_cache(maxsize=8, ttl_seconds=300)
        def add(a, b):
            nonlocal call_count; call_count += 1; return a + b
        assert add(1, 2) == 3
        assert add(1, 2) == 3
        assert call_count == 1

class TestMeasureExecution:
    def test_decorator(self):
        from src.utils.performance import measure_execution_time
        @measure_execution_time
        def dummy(): return 42
        assert dummy() == 42

class TestLazyLoader:
    def test_lazy_init(self):
        from src.utils.performance import LazyLoader
        loader = LazyLoader(lambda: {"k": "v"})
        assert loader.is_loaded is False
        assert loader.get() == {"k": "v"}
        assert loader.is_loaded is True

    def test_reset(self):
        from src.utils.performance import LazyLoader
        loader = LazyLoader(lambda: 99)
        loader.get()
        loader.reset()
        assert loader.is_loaded is False

class TestPerfMetrics:
    def test_metrics(self):
        from src.utils.performance import get_performance_metrics
        m = get_performance_metrics()
        assert "timestamp" in m
        assert m["cache_status"] == "active"

# ── Accessibility Tests ──────────────────────────────────────────
class TestAccessibility:
    def test_skip_nav(self):
        from src.utils.accessibility import SKIP_NAV_HTML
        assert "skip-nav" in SKIP_NAV_HTML
        assert "main-content" in SKIP_NAV_HTML

    def test_skip_nav_css(self):
        from src.utils.accessibility import SKIP_NAV_CSS
        assert "skip-nav" in SKIP_NAV_CSS
        assert "prefers-reduced-motion" in SKIP_NAV_CSS

    def test_main_wrapper(self):
        from src.utils.accessibility import get_main_content_wrapper
        h = get_main_content_wrapper("<p>Hi</p>")
        assert 'role="main"' in h
        assert 'id="main-content"' in h

    def test_nav_landmark(self):
        from src.utils.accessibility import get_nav_landmark
        h = get_nav_landmark("<ul></ul>")
        assert 'role="navigation"' in h

    def test_live_region(self):
        from src.utils.accessibility import get_live_region
        h = get_live_region("Done!")
        assert 'aria-live="polite"' in h

    def test_form_field(self):
        from src.utils.accessibility import get_form_field_html
        h = get_form_field_html("pin", "PIN", required=True)
        assert 'aria-required="true"' in h

    def test_form_field_error(self):
        from src.utils.accessibility import get_form_field_html
        h = get_form_field_html("x", "X", error_text="Bad")
        assert 'aria-invalid="true"' in h
        assert 'role="alert"' in h

    def test_contrast_pass(self):
        from src.utils.accessibility import check_contrast_ratio
        r = check_contrast_ratio("#ffffff", "#000000")
        assert r["aa_pass"] is True
        assert r["aaa_pass"] is True
        assert r["ratio"] == 21.0

    def test_contrast_fail(self):
        from src.utils.accessibility import check_contrast_ratio
        r = check_contrast_ratio("#cccccc", "#ffffff")
        assert r["aa_pass"] is False

# ── Vertex AI Service Tests ──────────────────────────────────────
class TestVertexAI:
    def test_verify_claim_fallback(self):
        from src.services.vertex_ai_service import ai_verify_claim
        r = ai_verify_claim("Test claim")
        assert r["verdict"] in ("PENDING", "AI-VERIFIED")
        assert "source" in r

    def test_answer_query_fallback(self):
        from src.services.vertex_ai_service import ai_answer_voter_query
        a = ai_answer_voter_query("How to vote?")
        assert len(a) > 0

    def test_content_safety_safe(self):
        from src.services.vertex_ai_service import ai_classify_content_safety
        r = ai_classify_content_safety("How to register?")
        assert r["safe"] is True

    def test_content_safety_unsafe(self):
        from src.services.vertex_ai_service import ai_classify_content_safety
        r = ai_classify_content_safety("violence threat")
        assert r["safe"] is False

    def test_health_check(self):
        from src.services.vertex_ai_service import get_ai_service_health
        h = get_ai_service_health()
        assert "status" in h

    def test_service_name(self):
        from src.services.vertex_ai_service import VertexAIService
        s = VertexAIService()
        assert s.service_name == "Google Vertex AI (Gemini)"

# ── BigQuery Service Tests ───────────────────────────────────────
class TestBigQuery:
    def test_track_event(self):
        from src.services.bigquery_service import track_event
        assert track_event("test_event", {"key": "val"}) is True

    def test_analytics_summary(self):
        from src.services.bigquery_service import track_event, get_analytics_summary
        track_event("summary_test")
        s = get_analytics_summary()
        assert s["total_events"] >= 1
        assert "event_counts" in s

    def test_feature_usage(self):
        from src.services.bigquery_service import get_feature_usage_report
        r = get_feature_usage_report()
        assert isinstance(r, list)
        assert all("feature" in x for x in r)

    def test_regional_engagement(self):
        from src.services.bigquery_service import track_event, get_regional_engagement
        track_event("reg_test", {"state": "Delhi"})
        e = get_regional_engagement()
        assert isinstance(e, dict)

    def test_health(self):
        from src.services.bigquery_service import get_bigquery_service_health
        h = get_bigquery_service_health()
        assert "status" in h

    def test_service_name(self):
        from src.services.bigquery_service import BigQueryService
        s = BigQueryService()
        assert s.service_name == "Google BigQuery"

# ── Base Service Tests ───────────────────────────────────────────
class TestBaseService:
    def test_abstract(self):
        from src.services.base_service import BaseCloudService
        with pytest.raises(TypeError):
            BaseCloudService()

    def test_concrete(self):
        from src.services.vertex_ai_service import VertexAIService
        s = VertexAIService()
        assert s.is_initialized is False

# ── Translation Tests ────────────────────────────────────────────
class TestTranslations:
    def test_english(self):
        from src.utils.translations import t
        assert "Election" in t("hero_title", "en")

    def test_hindi(self):
        from src.utils.translations import t
        r = t("hero_title", "hi")
        assert len(r) > 0

    def test_missing_key(self):
        from src.utils.translations import t
        r = t("nonexistent_key", "en")
        assert r == "nonexistent_key"

    def test_lang_code(self):
        from src.utils.translations import get_lang_code
        assert get_lang_code("English") == "en"
        assert get_lang_code("हिन्दी (Hindi)") == "hi"
