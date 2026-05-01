"""
tests/test_app.py — Unit Tests for Citizen Election Assistant

Tests cover: input sanitization, roadmap generation, ballot simulation,
myth verification, and prompt formatting logic.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from engine import sanitize_input, generate_roadmap, simulate_ballot, check_myth, get_evm_candidates
from prompts import (
    build_roadmap_prompt, build_myth_check_prompt,
    build_ballot_explainer_prompt, build_eligibility_prompt,
    SYSTEM_PROMPT, PROMPT_REGISTRY,
)


# ---------------------------------------------------------------------------
# Input Sanitization Tests
# ---------------------------------------------------------------------------

class TestSanitizeInput:
    """Tests for the sanitize_input security function."""

    def test_strips_html_tags(self) -> None:
        assert "<script>" not in sanitize_input("<script>alert('xss')</script>")

    def test_removes_script_patterns(self) -> None:
        result = sanitize_input("javascript:void(0)")
        assert "javascript" not in result.lower()

    def test_removes_event_handlers(self) -> None:
        result = sanitize_input('onerror=alert(1)')
        assert "onerror" not in result.lower()

    def test_escapes_html_entities(self) -> None:
        result = sanitize_input("5 > 3 & 2 < 4")
        assert "&gt;" in result or ">" not in result.replace("&gt;", "")

    def test_enforces_max_length(self) -> None:
        long_text = "A" * 1000
        assert len(sanitize_input(long_text, max_length=500)) == 500

    def test_handles_empty_string(self) -> None:
        assert sanitize_input("") == ""

    def test_handles_non_string(self) -> None:
        assert sanitize_input(None) == ""
        assert sanitize_input(123) == ""

    def test_strips_null_bytes(self) -> None:
        assert "\x00" not in sanitize_input("hello\x00world")

    def test_normal_text_unchanged(self) -> None:
        assert sanitize_input("Hello World") == "Hello World"


# ---------------------------------------------------------------------------
# Roadmap Generation Tests
# ---------------------------------------------------------------------------

class TestGenerateRoadmap:
    """Tests for the roadmap generation logic."""

    def test_eligible_voter(self) -> None:
        result = generate_roadmap("Delhi", 25)
        assert result["eligible"] is True
        assert len(result["steps"]) > 0
        assert "documents" in result

    def test_underage_voter(self) -> None:
        result = generate_roadmap("Maharashtra", 16)
        assert result["eligible"] is False
        assert "Not Yet Eligible" in result["title"]

    def test_exactly_18(self) -> None:
        result = generate_roadmap("Karnataka", 18)
        assert result["eligible"] is True

    def test_state_specific_info(self) -> None:
        result = generate_roadmap("Delhi", 20)
        assert result["state_info"] is not None

    def test_unknown_state(self) -> None:
        result = generate_roadmap("UnknownState", 20)
        assert result["eligible"] is True
        assert result["state_info"] is None

    def test_roadmap_has_tips(self) -> None:
        result = generate_roadmap("Tamil Nadu", 30)
        assert len(result["tips"]) > 0

    def test_documents_present(self) -> None:
        result = generate_roadmap("Gujarat", 22)
        docs = result["documents"]
        assert "Identity Proof (any one)" in docs
        assert "Address Proof (any one)" in docs


# ---------------------------------------------------------------------------
# Ballot Simulator Tests
# ---------------------------------------------------------------------------

class TestSimulateBallot:
    """Tests for the EVM/VVPAT ballot simulation."""

    def test_valid_vote(self) -> None:
        candidates = get_evm_candidates()
        result = simulate_ballot(0, candidates)
        assert result["success"] is True
        assert result["vvpat_match"] is True
        assert result["error"] is None

    def test_nota_vote(self) -> None:
        candidates = get_evm_candidates()
        nota_idx = len(candidates) - 1
        result = simulate_ballot(nota_idx, candidates)
        assert result["success"] is True
        assert "NOTA" in result["selected_candidate"]

    def test_invalid_index_negative(self) -> None:
        candidates = get_evm_candidates()
        result = simulate_ballot(-1, candidates)
        assert result["success"] is False
        assert result["error"] is not None

    def test_invalid_index_overflow(self) -> None:
        candidates = get_evm_candidates()
        result = simulate_ballot(99, candidates)
        assert result["success"] is False

    def test_empty_candidates(self) -> None:
        result = simulate_ballot(0, [])
        assert result["success"] is False

    def test_vvpat_explanation_present(self) -> None:
        candidates = get_evm_candidates()
        result = simulate_ballot(1, candidates)
        assert "VVPAT" in result["vvpat_explanation"]

    def test_evm_explanation_present(self) -> None:
        candidates = get_evm_candidates()
        result = simulate_ballot(0, candidates)
        assert "EVM" in result["evm_explanation"] or "beep" in result["evm_explanation"]


# ---------------------------------------------------------------------------
# Myth Buster Tests
# ---------------------------------------------------------------------------

class TestCheckMyth:
    """Tests for the myth verification engine."""

    def test_known_myth_evm_hack(self) -> None:
        result = check_myth("Can EVMs be hacked?")
        assert result["found"] is True
        assert result["verdict"] == "FALSE"

    def test_known_myth_nota(self) -> None:
        result = check_myth("NOTA can defeat a candidate")
        assert result["found"] is True
        assert result["verdict"] == "FALSE"

    def test_known_myth_voter_id(self) -> None:
        result = check_myth("Do I need a voter ID to vote?")
        assert result["found"] is True

    def test_unknown_myth(self) -> None:
        result = check_myth("aliens control elections")
        assert result["found"] is False

    def test_empty_claim(self) -> None:
        result = check_myth("")
        assert result["found"] is False

    def test_all_myths_returned(self) -> None:
        result = check_myth("anything")
        assert len(result["all_myths"]) > 0

    def test_ink_myth(self) -> None:
        result = check_myth("Does the ink wear off quickly?")
        assert result["found"] is True
        assert result["verdict"] == "FALSE"


# ---------------------------------------------------------------------------
# Prompt Formatting Tests
# ---------------------------------------------------------------------------

class TestPromptFormatting:
    """Tests for prompt builder functions."""

    def test_roadmap_prompt_contains_state(self) -> None:
        prompt = build_roadmap_prompt("Kerala", 25)
        assert "Kerala" in prompt
        assert "25" in prompt

    def test_roadmap_prompt_contains_system(self) -> None:
        prompt = build_roadmap_prompt("Goa", 30)
        assert "Chain-of-Thought" in prompt

    def test_myth_prompt_contains_claim(self) -> None:
        prompt = build_myth_check_prompt("EVMs can be hacked")
        assert "EVMs can be hacked" in prompt

    def test_myth_prompt_requests_verdict(self) -> None:
        prompt = build_myth_check_prompt("test claim")
        assert "verdict" in prompt.lower()

    def test_ballot_prompt_stages(self) -> None:
        for stage in ["overview", "evm", "vvpat", "counting"]:
            prompt = build_ballot_explainer_prompt(stage)
            assert "Chain-of-Thought" in prompt
            assert len(prompt) > 100

    def test_ballot_prompt_unknown_stage(self) -> None:
        prompt = build_ballot_explainer_prompt("unknown")
        assert "general Indian election" in prompt

    def test_eligibility_prompt_with_id(self) -> None:
        prompt = build_eligibility_prompt(25, True)
        assert "already has a Voter ID" in prompt

    def test_eligibility_prompt_without_id(self) -> None:
        prompt = build_eligibility_prompt(17, False)
        assert "does NOT have a Voter ID" in prompt

    def test_system_prompt_exists(self) -> None:
        assert len(SYSTEM_PROMPT) > 100
        assert "Citizen Election Assistant" in SYSTEM_PROMPT

    def test_prompt_registry_complete(self) -> None:
        assert "roadmap" in PROMPT_REGISTRY
        assert "myth_check" in PROMPT_REGISTRY
        assert "ballot_explainer" in PROMPT_REGISTRY
        assert "eligibility" in PROMPT_REGISTRY

    def test_registry_has_required_keys(self) -> None:
        for name, meta in PROMPT_REGISTRY.items():
            assert "builder" in meta
            assert "description" in meta
            assert "required_fields" in meta
