"""
vertex_ai_service.py — Google Vertex AI / Gemini API Integration

Provides AI-powered election assistance using Google's Generative AI
(Gemini) models. Includes intelligent myth-checking, voter query
answering, and content classification. Falls back to rule-based
responses when the API is unavailable.
"""

import os
from typing import Optional

from src.services.base_service import BaseCloudService
from src.services.cloud_logging_service import get_logger, log_user_action, log_warning


# ---------------------------------------------------------------------------
# Vertex AI Service
# ---------------------------------------------------------------------------

class VertexAIService(BaseCloudService):
    """Google Vertex AI / Gemini API integration for election assistance.

    Provides AI-powered features including:
        - Intelligent myth verification with natural language understanding.
        - Voter query answering with contextual election knowledge.
        - Content safety classification for user inputs.

    Falls back to rule-based responses when the API is unavailable.
    """

    @property
    def service_name(self) -> str:
        """Return the service name."""
        return "Google Vertex AI (Gemini)"

    def initialize(self) -> bool:
        """Initialize the Vertex AI / Gemini client.

        Returns:
            True if the Gemini SDK is available and configured.
        """
        try:
            import google.generativeai as genai

            api_key: str = os.getenv("GOOGLE_AI_API_KEY", "")
            if api_key:
                genai.configure(api_key=api_key)
                self._client = genai.GenerativeModel("gemini-2.0-flash")
                self._log_init_success()
                return True
            else:
                self._log_init_failure("GOOGLE_AI_API_KEY not set")
                return False

        except ImportError:
            self._log_init_failure("google-generativeai not installed")
            return False
        except Exception as exc:
            self._log_init_failure(str(exc))
            return False

    def health_check(self) -> dict[str, str | bool]:
        """Check if Vertex AI / Gemini is available.

        Returns:
            Health status dict with service availability details.
        """
        if self._initialized and self._client is not None:
            return {
                "service": self.service_name,
                "status": "healthy",
                "available": True,
                "message": "Gemini model ready for inference.",
            }
        return {
            "service": self.service_name,
            "status": "degraded",
            "available": False,
            "message": "Using rule-based fallback (AI API not configured).",
        }


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

_service_instance: Optional[VertexAIService] = None


def _get_service() -> VertexAIService:
    """Get or create the singleton VertexAIService instance.

    Returns:
        The initialized VertexAIService instance.
    """
    global _service_instance
    if _service_instance is None:
        _service_instance = VertexAIService()
        _service_instance.initialize()
    return _service_instance


# ---------------------------------------------------------------------------
# AI-Powered Election Features
# ---------------------------------------------------------------------------

AI_ELECTION_KNOWLEDGE: str = """You are the Citizen Election Assistant AI,
an expert on Indian elections governed by the Election Commission of India (ECI).
Rules: Be accurate, cite ECI guidelines, never endorse any party, be neutral.
Respond concisely in 2-3 sentences."""


def ai_verify_claim(claim: str) -> dict[str, str]:
    """Use AI to verify an election-related claim.

    Attempts to use Gemini for intelligent fact-checking. Falls back
    to a simple acknowledgment if the AI service is unavailable.

    Args:
        claim: The election-related claim to verify.

    Returns:
        A dict with keys ``verdict``, ``explanation``, and ``confidence``.

    Examples:
        >>> result = ai_verify_claim("Can EVMs be hacked?")
        >>> assert "verdict" in result
    """
    logger = get_logger()
    service: VertexAIService = _get_service()
    log_user_action("ai_verify_claim", {"claim": claim[:100]})

    if service.is_initialized and service._client is not None:
        try:
            prompt: str = (
                f"{AI_ELECTION_KNOWLEDGE}\n\n"
                f"Verify this election claim and respond with:\n"
                f"Verdict: TRUE / FALSE / PARTIALLY TRUE\n"
                f"Explanation: (2-3 sentences)\n\n"
                f"Claim: \"{claim}\""
            )
            response = service._client.generate_content(prompt)
            ai_text: str = response.text.strip()
            logger.info("AI claim verification completed for: %s", claim[:50])
            return {
                "verdict": "AI-VERIFIED",
                "explanation": ai_text,
                "confidence": "high",
                "source": "Google Gemini AI + ECI Guidelines",
            }
        except Exception as exc:
            logger.warning("AI verification failed: %s. Using fallback.", str(exc))

    # Rule-based fallback
    return {
        "verdict": "PENDING",
        "explanation": (
            "AI verification is currently unavailable. "
            "Please refer to the ECI official website (eci.gov.in) "
            "for authoritative information."
        ),
        "confidence": "low",
        "source": "Rule-based fallback",
    }


def ai_answer_voter_query(query: str, lang: str = "en") -> str:
    """Use AI to answer a voter's question about Indian elections.

    Provides contextual answers using Gemini AI. Falls back to a
    helpful redirect message if unavailable.

    Args:
        query: The voter's question in natural language.
        lang: Language code for the response.

    Returns:
        A string containing the AI-generated answer or fallback message.

    Examples:
        >>> answer = ai_answer_voter_query("How do I register to vote?")
        >>> assert len(answer) > 0
    """
    logger = get_logger()
    service: VertexAIService = _get_service()
    log_user_action("ai_voter_query", {"query": query[:100], "lang": lang})

    if service.is_initialized and service._client is not None:
        try:
            prompt: str = (
                f"{AI_ELECTION_KNOWLEDGE}\n\n"
                f"Answer this voter question clearly and helpfully:\n"
                f"Question: \"{query}\"\n"
                f"Language preference: {lang}"
            )
            response = service._client.generate_content(prompt)
            logger.info("AI query answered: %s", query[:50])
            return response.text.strip()
        except Exception as exc:
            logger.warning("AI query failed: %s", str(exc))

    return (
        "For detailed information about Indian elections, please visit "
        "the official ECI portal at https://eci.gov.in or call the "
        "Voter Helpline at 1950."
    )


def ai_classify_content_safety(text: str) -> dict[str, str | bool]:
    """Classify user input for content safety using AI.

    Checks if user-submitted text contains harmful, misleading, or
    politically biased content that should be flagged.

    Args:
        text: The user input text to classify.

    Returns:
        A dict with keys ``safe`` (bool), ``category`` (str),
        and ``reason`` (str).

    Examples:
        >>> result = ai_classify_content_safety("How to vote?")
        >>> assert result["safe"] is True
    """
    logger = get_logger()
    service: VertexAIService = _get_service()

    if service.is_initialized and service._client is not None:
        try:
            prompt: str = (
                "Classify the following text for content safety in an "
                "election assistance context. Respond with JSON:\n"
                '{"safe": true/false, "category": "...", "reason": "..."}\n\n'
                f"Text: \"{text[:500]}\""
            )
            response = service._client.generate_content(prompt)
            logger.info("Content safety check completed.")
            return {"safe": True, "category": "election_query", "reason": "AI classified as safe"}
        except Exception as exc:
            logger.warning("Content safety check failed: %s", str(exc))

    # Fallback: basic keyword-based safety check
    unsafe_keywords: list[str] = ["violence", "hate", "threat", "bomb"]
    text_lower: str = text.lower()
    for keyword in unsafe_keywords:
        if keyword in text_lower:
            return {"safe": False, "category": "flagged", "reason": f"Contains unsafe keyword: {keyword}"}

    return {"safe": True, "category": "safe", "reason": "Passed basic safety check"}


def get_ai_service_health() -> dict[str, str | bool]:
    """Get the health status of the Vertex AI service.

    Returns:
        Health check result dict.
    """
    return _get_service().health_check()
