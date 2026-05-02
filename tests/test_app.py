"""
test_app.py — Comprehensive Test Suite for Citizen Election Assistant

Covers validators, election engine, prompt builder, and service mocks.
Targets 100% coverage of the modular ``src/`` package.
"""

import pytest
from unittest.mock import patch, MagicMock
from typing import Any


# ── Validator Tests ──────────────────────────────────────────────────


class TestSanitizeInput:
    """Tests for src.utils.validators.sanitize_input."""

    def test_strips_html_tags(self) -> None:
        from src.utils.validators import sanitize_input
        result = sanitize_input("<b>hello</b>")
        assert "hello" in result
        assert "<b>" not in result

    def test_strips_script_tag(self) -> None:
        from src.utils.validators import sanitize_input
        result = sanitize_input("<script>alert('x')</script>hello")
        assert "<script>" not in result
        assert "hello" in result

    def test_strips_whitespace(self) -> None:
        from src.utils.validators import sanitize_input
        assert sanitize_input("  hello world  ") == "hello world"

    def test_empty_string(self) -> None:
        from src.utils.validators import sanitize_input
        assert sanitize_input("") == ""

    def test_normal_text(self) -> None:
        from src.utils.validators import sanitize_input
        assert sanitize_input("Delhi") == "Delhi"

    def test_non_string_input(self) -> None:
        from src.utils.validators import sanitize_input
        assert sanitize_input(123) == ""  # type: ignore

    def test_max_length_enforced(self) -> None:
        from src.utils.validators import sanitize_input
        long_text = "a" * 1000
        result = sanitize_input(long_text, max_length=50)
        assert len(result) <= 50


class TestValidateAge:
    """Tests for src.utils.validators.validate_age."""

    def test_valid_age(self) -> None:
        from src.utils.validators import validate_age
        valid, msg = validate_age(25)
        assert valid is True
        assert "eligible" in msg.lower()

    def test_underage(self) -> None:
        from src.utils.validators import validate_age
        valid, msg = validate_age(15)
        assert valid is True  # validator returns True with message
        assert "not yet eligible" in msg.lower()

    def test_minimum_age(self) -> None:
        from src.utils.validators import validate_age
        valid, msg = validate_age(18)
        assert valid is True

    def test_negative_age(self) -> None:
        from src.utils.validators import validate_age
        valid, msg = validate_age(-1)
        assert not valid
        assert "positive" in msg.lower()

    def test_zero_age(self) -> None:
        from src.utils.validators import validate_age
        valid, msg = validate_age(0)
        assert not valid

    def test_max_boundary(self) -> None:
        from src.utils.validators import validate_age
        valid, msg = validate_age(120)
        assert valid

    def test_over_max_boundary(self) -> None:
        from src.utils.validators import validate_age
        valid, msg = validate_age(150)
        assert not valid
        assert "realistic" in msg.lower()


class TestValidateState:
    """Tests for src.utils.validators.validate_state."""

    def test_valid_state(self) -> None:
        from src.utils.validators import validate_state
        from src.logic.election_engine import INDIAN_STATES
        assert validate_state("Delhi", INDIAN_STATES) == (True, "Valid state/UT.")

    def test_invalid_state(self) -> None:
        from src.utils.validators import validate_state
        from src.logic.election_engine import INDIAN_STATES
        valid, msg = validate_state("Atlantis", INDIAN_STATES)
        assert not valid
        assert "Unknown" in msg

    def test_empty_state(self) -> None:
        from src.utils.validators import validate_state
        valid, msg = validate_state("", [])
        assert not valid
        assert "empty" in msg.lower()

    def test_case_insensitive(self) -> None:
        from src.utils.validators import validate_state
        valid, msg = validate_state("delhi", ["Delhi"])
        assert valid


class TestValidateZipCode:
    """Tests for src.utils.validators.validate_zip_code."""

    def test_valid_pincode(self) -> None:
        from src.utils.validators import validate_zip_code
        assert validate_zip_code("110001") == (True, "Valid PIN code.")

    def test_invalid_short(self) -> None:
        from src.utils.validators import validate_zip_code
        valid, msg = validate_zip_code("1234")
        assert not valid

    def test_invalid_alpha(self) -> None:
        from src.utils.validators import validate_zip_code
        valid, msg = validate_zip_code("abcdef")
        assert not valid

    def test_empty_pincode(self) -> None:
        from src.utils.validators import validate_zip_code
        valid, msg = validate_zip_code("")
        assert not valid

    def test_starts_with_zero(self) -> None:
        from src.utils.validators import validate_zip_code
        valid, msg = validate_zip_code("012345")
        assert not valid


# ── Election Engine Tests ────────────────────────────────────────────


class TestGenerateRoadmap:
    """Tests for src.logic.election_engine.generate_roadmap."""

    @patch("src.logic.election_engine.log_user_action")
    def test_eligible_voter(self, mock_log: MagicMock) -> None:
        from src.logic.election_engine import generate_roadmap
        result: dict = generate_roadmap("Delhi", 25)
        assert result["eligible"] is True
        assert len(result["steps"]) == 8
        assert "documents" in result
        assert len(result["tips"]) > 0

    @patch("src.logic.election_engine.log_user_action")
    def test_underage_voter(self, mock_log: MagicMock) -> None:
        from src.logic.election_engine import generate_roadmap
        result: dict = generate_roadmap("Delhi", 16)
        assert result["eligible"] is False
        assert len(result["steps"]) == 3

    @patch("src.logic.election_engine.log_user_action")
    def test_exactly_18(self, mock_log: MagicMock) -> None:
        from src.logic.election_engine import generate_roadmap
        result: dict = generate_roadmap("Karnataka", 18)
        assert result["eligible"] is True

    @patch("src.logic.election_engine.log_user_action")
    def test_state_info_present(self, mock_log: MagicMock) -> None:
        from src.logic.election_engine import generate_roadmap
        result: dict = generate_roadmap("Maharashtra", 22)
        assert result["state_info"] is not None
        assert "website" in result["state_info"]

    @patch("src.logic.election_engine.log_user_action")
    def test_state_info_absent(self, mock_log: MagicMock) -> None:
        from src.logic.election_engine import generate_roadmap
        result: dict = generate_roadmap("Goa", 30)
        assert result["state_info"] is None


class TestSimulateBallot:
    """Tests for src.logic.election_engine.simulate_ballot."""

    @patch("src.logic.election_engine.log_user_action")
    def test_valid_vote(self, mock_log: MagicMock) -> None:
        from src.logic.election_engine import simulate_ballot, get_evm_candidates
        candidates: list[str] = get_evm_candidates()
        result: dict = simulate_ballot(0, candidates)
        assert result["success"] is True
        assert result["vvpat_match"] is True
        assert result["error"] is None
        assert candidates[0] in result["selected_candidate"]

    @patch("src.logic.election_engine.log_user_action")
    def test_nota_vote(self, mock_log: MagicMock) -> None:
        from src.logic.election_engine import simulate_ballot, get_evm_candidates
        candidates: list[str] = get_evm_candidates()
        nota_idx: int = len(candidates) - 1
        result: dict = simulate_ballot(nota_idx, candidates)
        assert result["success"] is True
        assert "NOTA" in result["evm_explanation"]

    def test_invalid_index(self) -> None:
        from src.logic.election_engine import simulate_ballot, get_evm_candidates
        candidates: list[str] = get_evm_candidates()
        result: dict = simulate_ballot(99, candidates)
        assert result["success"] is False
        assert result["error"] is not None

    def test_negative_index(self) -> None:
        from src.logic.election_engine import simulate_ballot, get_evm_candidates
        candidates: list[str] = get_evm_candidates()
        result: dict = simulate_ballot(-1, candidates)
        assert result["success"] is False

    def test_empty_candidates(self) -> None:
        from src.logic.election_engine import simulate_ballot
        result: dict = simulate_ballot(0, [])
        assert result["success"] is False
        assert "No candidates" in result["error"]


class TestCheckMyth:
    """Tests for src.logic.election_engine.check_myth."""

    @patch("src.logic.election_engine.log_user_action")
    def test_evm_hack_myth(self, mock_log: MagicMock) -> None:
        from src.logic.election_engine import check_myth
        result: dict = check_myth("Can EVMs be hacked?")
        assert result["found"] is True
        assert result["verdict"] == "FALSE"
        assert "EVM" in result["myth"]

    @patch("src.logic.election_engine.log_user_action")
    def test_nota_myth(self, mock_log: MagicMock) -> None:
        from src.logic.election_engine import check_myth
        result: dict = check_myth("NOTA can defeat candidates")
        assert result["found"] is True
        assert result["verdict"] == "FALSE"

    @patch("src.logic.election_engine.log_user_action")
    def test_no_match(self, mock_log: MagicMock) -> None:
        from src.logic.election_engine import check_myth
        result: dict = check_myth("random gibberish xyz")
        assert result["found"] is False

    def test_empty_claim(self) -> None:
        from src.logic.election_engine import check_myth
        result: dict = check_myth("")
        assert result["found"] is False
        assert "enter a claim" in result["explanation"].lower()

    @patch("src.logic.election_engine.log_user_action")
    def test_returns_all_myths(self, mock_log: MagicMock) -> None:
        from src.logic.election_engine import check_myth
        result: dict = check_myth("voting compulsory")
        assert len(result["all_myths"]) > 10


# ── Prompt Builder Tests ─────────────────────────────────────────────


class TestPromptBuilder:
    """Tests for src.logic.prompt_builder functions."""

    def test_roadmap_prompt(self) -> None:
        from src.logic.prompt_builder import build_roadmap_prompt
        prompt: str = build_roadmap_prompt("Delhi", 22)
        assert "Delhi" in prompt
        assert "22" in prompt
        assert "Chain-of-Thought" in prompt

    def test_myth_check_prompt(self) -> None:
        from src.logic.prompt_builder import build_myth_check_prompt
        prompt: str = build_myth_check_prompt("EVMs hacked")
        assert "EVMs hacked" in prompt
        assert "verdict" in prompt.lower()

    def test_ballot_explainer_prompt_evm(self) -> None:
        from src.logic.prompt_builder import build_ballot_explainer_prompt
        prompt: str = build_ballot_explainer_prompt("evm")
        assert "Electronic Voting Machine" in prompt

    def test_ballot_explainer_prompt_unknown(self) -> None:
        from src.logic.prompt_builder import build_ballot_explainer_prompt
        prompt: str = build_ballot_explainer_prompt("unknown_stage")
        assert "general" in prompt.lower()

    def test_eligibility_prompt_with_id(self) -> None:
        from src.logic.prompt_builder import build_eligibility_prompt
        prompt: str = build_eligibility_prompt(25, True)
        assert "already has" in prompt

    def test_eligibility_prompt_without_id(self) -> None:
        from src.logic.prompt_builder import build_eligibility_prompt
        prompt: str = build_eligibility_prompt(16, False)
        assert "does NOT have" in prompt

    def test_prompt_registry(self) -> None:
        from src.logic.prompt_builder import PROMPT_REGISTRY
        assert "roadmap" in PROMPT_REGISTRY
        assert "myth_check" in PROMPT_REGISTRY
        assert len(PROMPT_REGISTRY) >= 4


# ── Cloud Logging Service Tests ──────────────────────────────────────


class TestCloudLoggingService:
    """Tests for src.services.cloud_logging_service."""

    def test_get_logger_returns_logger(self) -> None:
        from src.services.cloud_logging_service import get_logger
        logger = get_logger()
        assert logger is not None
        assert hasattr(logger, "info")

    def test_log_user_action_does_not_raise(self) -> None:
        from src.services.cloud_logging_service import log_user_action
        log_user_action("test_action", {"key": "value"})

    def test_log_user_action_minimal(self) -> None:
        from src.services.cloud_logging_service import log_user_action
        log_user_action("test", {})


# ── Static Data Tests ────────────────────────────────────────────────


class TestStaticData:
    """Tests for cached static data accessors."""

    def test_get_states_sorted(self) -> None:
        from src.logic.election_engine import get_states
        states: list[str] = get_states()
        assert len(states) > 30
        assert states == sorted(states)

    def test_get_required_documents(self) -> None:
        from src.logic.election_engine import get_required_documents
        docs: dict = get_required_documents()
        assert "Identity Proof (any one)" in docs
        assert len(docs) >= 4

    def test_get_election_myths(self) -> None:
        from src.logic.election_engine import get_election_myths
        myths: list = get_election_myths()
        assert len(myths) >= 15
        for m in myths:
            assert "myth" in m
            assert "verdict" in m
            assert "explanation" in m
            assert "source" in m

    def test_get_evm_candidates(self) -> None:
        from src.logic.election_engine import get_evm_candidates
        candidates: list[str] = get_evm_candidates()
        assert len(candidates) == 5
        assert any("NOTA" in c for c in candidates)

    def test_state_specific_info(self) -> None:
        from src.logic.election_engine import get_state_specific_info
        info: dict = get_state_specific_info()
        assert "Delhi" in info
        assert "helpline" in info["Delhi"]
