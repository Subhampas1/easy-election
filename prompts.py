"""
prompts.py — System Prompts for Citizen Election Assistant

Contains Chain-of-Thought (CoT) prompt templates used to generate
structured election guidance. All prompts are built via type-hinted
factory functions to ensure consistency and testability.
"""

from typing import Optional


# ---------------------------------------------------------------------------
# Master System Prompt (Chain-of-Thought)
# ---------------------------------------------------------------------------

SYSTEM_PROMPT: str = """
You are the **Citizen Election Assistant**, an expert on the Indian electoral
process governed by the Election Commission of India (ECI).

## Your Guiding Principles
1. **Accuracy** — cite only official ECI rules, the Representation of the
   People Act 1951, and Supreme Court rulings.
2. **Clarity** — explain complex legal language in simple, everyday terms.
3. **Neutrality** — never endorse any political party or candidate.
4. **Empathy** — be patient with first-time voters and senior citizens.

## Chain-of-Thought Reasoning
For every query, follow this internal reasoning chain before answering:
  Step 1 → Identify the user's demographic context (state, age, ID status).
  Step 2 → Map their situation to the relevant ECI guidelines.
  Step 3 → Generate an actionable, numbered checklist.
  Step 4 → Add helpful tips and common pitfalls to avoid.
  Step 5 → Summarize in one sentence.

Always output in the requested structured format.
"""


# ---------------------------------------------------------------------------
# Prompt Builders
# ---------------------------------------------------------------------------

def build_roadmap_prompt(state: str, age: int) -> str:
    """Build a personalized election-readiness prompt.

    Uses Chain-of-Thought to guide the model through demographic analysis
    before producing a step-by-step voter registration checklist.

    Args:
        state: The Indian state/UT the user resides in.
        age: The user's current age in years.

    Returns:
        A formatted prompt string ready for LLM consumption.
    """
    return (
        f"{SYSTEM_PROMPT}\n\n"
        f"## User Context\n"
        f"- **State / UT:** {state}\n"
        f"- **Age:** {age} years\n\n"
        f"## Task\n"
        f"Using your Chain-of-Thought reasoning:\n"
        f"1. Determine if the user is eligible to vote (minimum age 18).\n"
        f"2. List the documents required for voter registration in {state}.\n"
        f"3. Provide a numbered checklist of steps from registration to polling day.\n"
        f"4. Mention any state-specific rules or deadlines.\n"
        f"5. Summarize the entire process in one sentence.\n\n"
        f"Respond in **structured markdown** with clear headings."
    )


def build_myth_check_prompt(claim: str) -> str:
    """Build a fact-checking prompt for an election-related claim.

    Instructs the model to reason step-by-step before delivering a
    verdict of TRUE, FALSE, or PARTIALLY TRUE.

    Args:
        claim: The election-related claim to verify.

    Returns:
        A formatted prompt string for myth verification.
    """
    return (
        f"{SYSTEM_PROMPT}\n\n"
        f"## Claim to Verify\n"
        f'"{claim}"\n\n'
        f"## Task\n"
        f"Using your Chain-of-Thought reasoning:\n"
        f"1. Restate the claim in neutral terms.\n"
        f"2. Identify the relevant ECI rule or legal provision.\n"
        f"3. Compare the claim against the official guideline.\n"
        f"4. Deliver a verdict: **TRUE**, **FALSE**, or **PARTIALLY TRUE**.\n"
        f"5. Explain the reasoning in 2-3 sentences.\n\n"
        f"Respond with a JSON-like structure:\n"
        f"  verdict: ...\n"
        f"  explanation: ...\n"
        f"  source: ..."
    )


def build_ballot_explainer_prompt(stage: str) -> str:
    """Build an explanatory prompt for a specific ballot/EVM stage.

    Args:
        stage: One of 'overview', 'evm', 'vvpat', 'counting'.

    Returns:
        A formatted prompt string explaining the given stage.
    """
    stage_descriptions: dict[str, str] = {
        "overview": "the complete journey of a vote from button-press to result declaration",
        "evm": "how the Electronic Voting Machine (EVM) works internally",
        "vvpat": "how the Voter Verifiable Paper Audit Trail (VVPAT) confirms the vote",
        "counting": "how votes are counted and results are declared",
    }

    description: str = stage_descriptions.get(
        stage.lower(),
        "the general Indian election voting process"
    )

    return (
        f"{SYSTEM_PROMPT}\n\n"
        f"## Task\n"
        f"Explain {description}.\n\n"
        f"Use Chain-of-Thought reasoning:\n"
        f"1. Start with what the voter sees.\n"
        f"2. Explain the underlying mechanism step by step.\n"
        f"3. Address common concerns (e.g., tampering, privacy).\n"
        f"4. End with a reassuring summary.\n\n"
        f"Keep the language simple — assume the reader is a first-time voter."
    )


def build_eligibility_prompt(age: int, has_voter_id: bool) -> str:
    """Build a prompt to check voter eligibility and next steps.

    Args:
        age: The user's age in years.
        has_voter_id: Whether the user already possesses a Voter ID (EPIC).

    Returns:
        A formatted prompt string for eligibility analysis.
    """
    id_status: str = "already has a Voter ID (EPIC)" if has_voter_id else "does NOT have a Voter ID yet"

    return (
        f"{SYSTEM_PROMPT}\n\n"
        f"## User Context\n"
        f"- **Age:** {age} years\n"
        f"- **Voter ID Status:** {id_status}\n\n"
        f"## Task\n"
        f"1. Confirm whether the user is eligible to vote.\n"
        f"2. If eligible but without ID — list steps to get one.\n"
        f"3. If under 18 — explain when they can register.\n"
        f"4. If already registered — provide polling-day tips.\n\n"
        f"Be encouraging and supportive in tone."
    )


# ---------------------------------------------------------------------------
# Prompt Metadata (for testing & validation)
# ---------------------------------------------------------------------------

PROMPT_REGISTRY: dict[str, dict[str, str]] = {
    "roadmap": {
        "builder": "build_roadmap_prompt",
        "description": "Generates a personalized voter registration checklist.",
        "required_fields": "state, age",
    },
    "myth_check": {
        "builder": "build_myth_check_prompt",
        "description": "Fact-checks an election-related claim.",
        "required_fields": "claim",
    },
    "ballot_explainer": {
        "builder": "build_ballot_explainer_prompt",
        "description": "Explains a stage of the EVM/VVPAT process.",
        "required_fields": "stage",
    },
    "eligibility": {
        "builder": "build_eligibility_prompt",
        "description": "Checks voter eligibility and advises next steps.",
        "required_fields": "age, has_voter_id",
    },
}
