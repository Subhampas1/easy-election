"""
validators.py — Input Validation and Sanitization Utilities

Provides security-focused input processing for all user-facing text fields.
Includes XSS prevention, injection filtering, and domain-specific validators
for Indian election data (age, state, PIN code).
"""

import re
import html
from typing import Optional


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

INDIAN_PIN_CODE_PATTERN: re.Pattern[str] = re.compile(r"^[1-9]\d{5}$")
"""Regex for valid Indian PIN codes: 6 digits, first digit non-zero."""

MAX_INPUT_LENGTH: int = 500
"""Default maximum allowed input length in characters."""

TRIVIAL_WORDS: frozenset[str] = frozenset({
    "the", "a", "an", "in", "is", "can", "be", "to", "of",
    "and", "or", "for", "not", "are", "you", "it", "that", "this",
})
"""Common stop words excluded from fuzzy matching scores."""


# ---------------------------------------------------------------------------
# Core Sanitization
# ---------------------------------------------------------------------------

def sanitize_input(text: str, max_length: int = MAX_INPUT_LENGTH) -> str:
    """Sanitize user input to prevent XSS and injection attacks.

    Strips HTML tags, escapes special characters, removes script patterns,
    and enforces a maximum length.

    Args:
        text: Raw user input string.
        max_length: Maximum allowed character count (default 500).

    Returns:
        A sanitized, safe string. Returns empty string for non-string inputs.

    Examples:
        >>> sanitize_input("<script>alert('xss')</script>")
        "alert(&#x27;xss&#x27;)"
        >>> sanitize_input("Hello World")
        "Hello World"
    """
    if not isinstance(text, str):
        return ""

    # Strip leading/trailing whitespace
    text = text.strip()

    # Remove HTML tags
    text = re.sub(r"<[^>]*>", "", text)

    # Remove script-like patterns (case-insensitive)
    text = re.sub(r"(?i)(javascript|on\w+\s*=|script)", "", text)

    # Escape HTML entities
    text = html.escape(text, quote=True)

    # Remove null bytes and control characters
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", text)

    # Enforce max length
    text = text[:max_length]

    return text


# ---------------------------------------------------------------------------
# Domain-Specific Validators
# ---------------------------------------------------------------------------

def validate_age(age: int) -> tuple[bool, str]:
    """Validate a voter's age for Indian elections.

    Checks that the age is a reasonable positive integer. The minimum
    voting age in India is 18, but this validator accepts all ages and
    returns appropriate messages.

    Args:
        age: The user's age in years.

    Returns:
        A tuple of (is_valid, message). ``is_valid`` is True if the age
        is within the acceptable range (1–120). ``message`` provides
        context about eligibility or the validation error.

    Examples:
        >>> validate_age(25)
        (True, "Eligible to vote.")
        >>> validate_age(16)
        (True, "Not yet eligible. 2 year(s) until voting age.")
        >>> validate_age(-1)
        (False, "Age must be a positive number.")
    """
    if not isinstance(age, int):
        return False, "Age must be an integer."

    if age <= 0:
        return False, "Age must be a positive number."

    if age > 120:
        return False, "Please enter a realistic age (1–120)."

    if age < 18:
        years_left: int = 18 - age
        return True, f"Not yet eligible. {years_left} year(s) until voting age."

    return True, "Eligible to vote."


def validate_zip_code(zip_code: str) -> tuple[bool, str]:
    """Validate an Indian PIN (postal) code.

    Indian PIN codes are exactly 6 digits, with the first digit
    ranging from 1 to 9 (never 0).

    Args:
        zip_code: The PIN code string to validate.

    Returns:
        A tuple of (is_valid, message). ``is_valid`` is True if the
        PIN code matches the expected format.

    Examples:
        >>> validate_zip_code("110001")
        (True, "Valid PIN code.")
        >>> validate_zip_code("00001")
        (False, "Invalid PIN code format. Must be 6 digits, first digit 1-9.")
    """
    if not isinstance(zip_code, str):
        return False, "PIN code must be a string."

    cleaned: str = zip_code.strip()

    if not cleaned:
        return False, "PIN code cannot be empty."

    if not cleaned.isdigit():
        return False, "PIN code must contain only digits."

    if len(cleaned) != 6:
        return False, f"PIN code must be exactly 6 digits (got {len(cleaned)})."

    if not INDIAN_PIN_CODE_PATTERN.match(cleaned):
        return False, "Invalid PIN code format. Must be 6 digits, first digit 1-9."

    return True, "Valid PIN code."


def validate_state(state: str, valid_states: list[str]) -> tuple[bool, str]:
    """Validate that a state name exists in the known list.

    Performs case-insensitive matching against the provided list of
    valid Indian states and union territories.

    Args:
        state: The state/UT name to validate.
        valid_states: List of accepted state/UT names.

    Returns:
        A tuple of (is_valid, message). ``is_valid`` is True if the
        state is found in the valid list.

    Examples:
        >>> validate_state("Delhi", ["Delhi", "Maharashtra"])
        (True, "Valid state/UT.")
        >>> validate_state("Atlantis", ["Delhi", "Maharashtra"])
        (False, "Unknown state/UT: 'Atlantis'.")
    """
    if not isinstance(state, str) or not state.strip():
        return False, "State name cannot be empty."

    cleaned: str = state.strip()
    lower_states: list[str] = [s.lower() for s in valid_states]

    if cleaned.lower() in lower_states:
        return True, "Valid state/UT."

    return False, f"Unknown state/UT: '{cleaned}'."
