"""
engine.py — Logic Engine for Citizen Election Assistant

Contains all business logic: roadmap generation, ballot simulation,
myth verification, input sanitization, and Google Maps integration.
All static election data is cached for performance.
"""

import re
import html
import os
import urllib.parse
from typing import Optional

import streamlit as st
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()


# ---------------------------------------------------------------------------
# Input Sanitization
# ---------------------------------------------------------------------------

def sanitize_input(text: str, max_length: int = 500) -> str:
    """Sanitize user input to prevent XSS and injection attacks.

    Strips HTML tags, escapes special characters, removes script patterns,
    and enforces a maximum length.

    Args:
        text: Raw user input string.
        max_length: Maximum allowed character count (default 500).

    Returns:
        A sanitized, safe string.
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
# Static Election Data (cached)
# ---------------------------------------------------------------------------

INDIAN_STATES: list[str] = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar",
    "Chhattisgarh", "Goa", "Gujarat", "Haryana", "Himachal Pradesh",
    "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra",
    "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab",
    "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura",
    "Uttar Pradesh", "Uttarakhand", "West Bengal",
    "Andaman & Nicobar Islands", "Chandigarh", "Dadra & Nagar Haveli and Daman & Diu",
    "Delhi", "Jammu & Kashmir", "Ladakh", "Lakshadweep", "Puducherry",
]

EVM_CANDIDATES_DEFAULT: list[str] = [
    "Party A — Candidate Alpha",
    "Party B — Candidate Beta",
    "Party C — Candidate Gamma",
    "Party D — Candidate Delta",
    "NOTA (None Of The Above)",
]


@st.cache_data
def get_states() -> list[str]:
    """Return the list of Indian states and union territories.

    Returns:
        Sorted list of state/UT names.
    """
    return sorted(INDIAN_STATES)


@st.cache_data
def get_required_documents() -> dict[str, list[str]]:
    """Return documents required for voter registration.

    Returns:
        Dict mapping document category to list of accepted documents.
    """
    return {
        "Identity Proof (any one)": [
            "Aadhaar Card",
            "PAN Card",
            "Driving License",
            "Passport",
            "Bank Passbook with Photo",
            "Government-issued Photo ID",
        ],
        "Address Proof (any one)": [
            "Aadhaar Card",
            "Utility Bill (electricity, water, gas)",
            "Bank Statement / Passbook",
            "Rent Agreement",
            "Ration Card",
            "Government-issued Address Proof",
        ],
        "Age Proof (any one)": [
            "Birth Certificate",
            "School Leaving Certificate / Marksheet",
            "Aadhaar Card",
            "PAN Card",
            "Passport",
        ],
        "Photographs": [
            "2 recent passport-size colour photographs",
        ],
    }


@st.cache_data
def get_election_myths() -> list[dict[str, str]]:
    """Return curated list of common election myths with verdicts.

    Returns:
        List of dicts with keys: myth, verdict, explanation, source.
    """
    return [
        {
            "myth": "EVMs can be hacked remotely",
            "verdict": "FALSE",
            "explanation": "EVMs are standalone devices with no wireless connectivity, Wi-Fi, Bluetooth, or internet connection. They use one-time programmable chips that cannot be reprogrammed once manufactured. The Election Commission conducts rigorous testing including first-level checking (FLC) before every election.",
            "source": "Election Commission of India — EVM FAQ",
        },
        {
            "myth": "You need a Voter ID card to vote",
            "verdict": "PARTIALLY TRUE",
            "explanation": "While the EPIC (Voter ID) is the primary document, the ECI accepts 12 alternative photo IDs including Aadhaar, Passport, Driving License, PAN Card, and others. Your name must be on the electoral roll regardless of which ID you carry.",
            "source": "ECI Order — Alternative Photo IDs for Voting",
        },
        {
            "myth": "NOTA vote can defeat a candidate",
            "verdict": "FALSE",
            "explanation": "Even if NOTA receives the highest number of votes, the candidate with the most votes among the contesting candidates wins. NOTA is counted but does not affect the result. However, it registers the voter's dissatisfaction officially.",
            "source": "Supreme Court Judgment — PUCL vs Union of India (2013)",
        },
        {
            "myth": "Voting is compulsory in India",
            "verdict": "FALSE",
            "explanation": "Voting is a constitutional right but not a legal obligation in India at the national level. However, some states like Gujarat have enacted laws making voting compulsory for local body elections. There is no penalty for not voting in general/state elections.",
            "source": "Article 326, Constitution of India",
        },
        {
            "myth": "You can vote from any polling station",
            "verdict": "FALSE",
            "explanation": "You can only vote at the specific polling station assigned to your address on the electoral roll. You cannot walk into any random polling booth. Check your assigned station on the NVSP portal or Voter Helpline app.",
            "source": "Section 62, Representation of the People Act 1951",
        },
        {
            "myth": "Postal ballots are only for military personnel",
            "verdict": "FALSE",
            "explanation": "Postal ballots are available for service voters (military, paramilitary), government employees on election duty, voters above 80 years of age, persons with disabilities, and voters under preventive detention. Senior citizens and PwD voters can opt for postal ballots.",
            "source": "ECI Guidelines on Postal Ballot",
        },
        {
            "myth": "NRIs cannot vote in Indian elections",
            "verdict": "FALSE",
            "explanation": "NRIs can register as overseas electors under Section 20A of the RP Act 1950 (amended in 2010). They must be present in their constituency on polling day to vote in person. E-postal ballot facility has been proposed but not yet fully implemented for all.",
            "source": "Section 20A, Representation of the People Act 1950",
        },
        {
            "myth": "The VVPAT slip can be taken home as proof",
            "verdict": "FALSE",
            "explanation": "The VVPAT slip is displayed behind a glass window for 7 seconds and then drops into a sealed box. Voters are NOT allowed to touch, photograph, or take the slip. The slips are sealed and stored for verification in case of disputes.",
            "source": "Rule 49MA, Conduct of Election Rules 1961",
        },
        {
            "myth": "Candidates with criminal cases cannot contest elections",
            "verdict": "FALSE",
            "explanation": "Only candidates CONVICTED and sentenced to 2+ years imprisonment are disqualified. Candidates with pending criminal cases (not yet convicted) can still contest elections. However, they must declare all pending cases in their nomination affidavit.",
            "source": "Section 8, Representation of the People Act 1951",
        },
        {
            "myth": "Election results can be challenged only by candidates",
            "verdict": "FALSE",
            "explanation": "Any elector (voter registered in that constituency) can file an election petition challenging results, not just the contesting candidates. The petition must be filed within 45 days of the result declaration before the High Court.",
            "source": "Section 81, Representation of the People Act 1951",
        },
        {
            "myth": "You must vote for a party, not a candidate",
            "verdict": "FALSE",
            "explanation": "In Indian elections, you vote for a CANDIDATE, not a party. The ballot/EVM shows candidate names alongside party symbols. Independent candidates also contest elections without any party affiliation.",
            "source": "Election Commission of India — Voter Education",
        },
        {
            "myth": "Booth capturing still happens in modern elections",
            "verdict": "PARTIALLY TRUE",
            "explanation": "While booth capturing has drastically reduced due to EVMs, CCTV surveillance, webcasting, and micro-observers, isolated incidents still occur in some regions. The ECI has strong countermeasures including re-polling in case of proven booth capture.",
            "source": "Section 135A, Representation of the People Act 1951",
        },
        {
            "myth": "The Election Commission can postpone elections indefinitely",
            "verdict": "FALSE",
            "explanation": "The ECI must conduct elections within the time frame specified by the Constitution. A new Lok Sabha must be constituted before the expiry of the current one (5 years). The ECI can reschedule polling in specific constituencies due to natural disasters or law & order situations but cannot postpone elections indefinitely.",
            "source": "Article 83 & 172, Constitution of India",
        },
        {
            "myth": "Ink on the finger wears off in a few hours",
            "verdict": "FALSE",
            "explanation": "The indelible ink used by ECI contains silver nitrate and is designed to last 2-4 weeks. It is applied on the left index finger's nail and cuticle. Attempts to remove it can cause skin damage. This prevents double voting.",
            "source": "Mysore Paints & Varnish Ltd. — ECI Ink Specification",
        },
        {
            "myth": "You can vote online in Indian elections",
            "verdict": "FALSE",
            "explanation": "As of now, India does not have an internet/online voting system for general or state elections. All voting is done either in person at polling stations or via postal ballot for eligible categories. Blockchain-based e-voting has been discussed but not implemented.",
            "source": "Election Commission of India — Official FAQ",
        },
    ]


@st.cache_data
def get_state_specific_info() -> dict[str, dict[str, str]]:
    """Return state-specific election details.

    Returns:
        Dict mapping state name to its election-relevant metadata.
    """
    return {
        "Delhi": {
            "chief_electoral_officer": "CEO Delhi Office",
            "helpline": "1950",
            "website": "https://ceodelhi.gov.in",
            "note": "Delhi has a separate State Election Commission for MCD elections.",
        },
        "Maharashtra": {
            "chief_electoral_officer": "CEO Maharashtra Office",
            "helpline": "1950",
            "website": "https://ceo.maharashtra.gov.in",
            "note": "Maharashtra uses online Form 6 for new registrations via NVSP.",
        },
        "Tamil Nadu": {
            "chief_electoral_officer": "CEO Tamil Nadu Office",
            "helpline": "1950",
            "website": "https://elections.tn.gov.in",
            "note": "Tamil Nadu provides voter slips in both Tamil and English.",
        },
        "Uttar Pradesh": {
            "chief_electoral_officer": "CEO UP Office",
            "helpline": "1950",
            "website": "https://ceouttarpradesh.nic.in",
            "note": "UP, being the largest state, has elections in multiple phases.",
        },
        "Karnataka": {
            "chief_electoral_officer": "CEO Karnataka Office",
            "helpline": "1950",
            "website": "https://ceo.karnataka.gov.in",
            "note": "Karnataka pioneered webcasting of polling stations.",
        },
    }


# ---------------------------------------------------------------------------
# Roadmap Generator
# ---------------------------------------------------------------------------

def generate_roadmap(state: str, age: int) -> dict:
    """Generate a personalized election-readiness roadmap.

    Analyzes the user's state and age to produce a step-by-step checklist
    covering eligibility, registration, documents, and voting day tips.

    Args:
        state: The Indian state/UT the user resides in.
        age: The user's current age in years.

    Returns:
        Dict with keys:
            - eligible (bool): Whether the user can vote.
            - title (str): Summary heading.
            - steps (list[dict]): Numbered checklist items.
            - documents (dict): Required documents by category.
            - tips (list[str]): Helpful voting tips.
            - state_info (dict | None): State-specific details if available.
    """
    state = sanitize_input(state)

    eligible: bool = age >= 18
    state_info: Optional[dict] = get_state_specific_info().get(state)

    if not eligible:
        return {
            "eligible": False,
            "title": f"You're {age} — Not Yet Eligible to Vote",
            "steps": [
                {"step": 1, "action": "Wait until you turn 18", "detail": f"You can register {18 - age} year(s) before your 18th birthday on the NVSP portal."},
                {"step": 2, "action": "Prepare your documents", "detail": "Gather your ID, address, and age proof documents now so you're ready."},
                {"step": 3, "action": "Learn about the process", "detail": "Use this app's Ballot Simulator to understand how voting works!"},
            ],
            "documents": get_required_documents(),
            "tips": [
                "You can apply for voter registration up to 1 year before turning 18.",
                "Download the Voter Helpline App to stay updated.",
                "Encourage eligible family members to verify their voter registration.",
            ],
            "state_info": state_info,
        }

    steps: list[dict[str, str | int]] = [
        {"step": 1, "action": "Check your name on the Electoral Roll", "detail": "Visit https://electoralsearch.eci.gov.in or use the Voter Helpline App (1950) to verify."},
        {"step": 2, "action": "Register if not enrolled", "detail": "Fill Form 6 online at https://voters.eci.gov.in or visit your nearest ERO office."},
        {"step": 3, "action": "Gather required documents", "detail": "Keep your identity proof, address proof, age proof, and passport photos ready."},
        {"step": 4, "action": "Receive your EPIC (Voter ID)", "detail": "After verification, your Voter ID card will be dispatched. Download the e-EPIC from the NVSP portal."},
        {"step": 5, "action": "Find your polling station", "detail": "Your assigned polling station is printed on your voter slip. Verify on the Voter Helpline App."},
        {"step": 6, "action": "Voting Day — Carry your ID", "detail": "Reach your polling station with a valid photo ID. Polling hours are typically 7 AM to 6 PM."},
        {"step": 7, "action": "Cast your vote", "detail": "Press the button next to your chosen candidate on the EVM. Verify on the VVPAT display (7 seconds)."},
        {"step": 8, "action": "Get inked!", "detail": "Your left index finger will be marked with indelible ink to prevent double voting."},
    ]

    tips: list[str] = [
        "Carry a valid photo ID — Voter ID, Aadhaar, Passport, or any of the 12 accepted IDs.",
        "Check your name on the electoral roll at least 2 weeks before election day.",
        "Reach the polling station early to avoid long queues.",
        "Voting is secret — no one can see whom you voted for.",
        "If you face any issues, contact the Booth Level Officer or call 1950.",
        "Voters above 80 or with disabilities can request a postal ballot.",
    ]

    if state_info:
        tips.append(f"For {state}-specific queries, visit: {state_info.get('website', 'N/A')}")

    return {
        "eligible": True,
        "title": f"Your Election Roadmap — {state}",
        "steps": steps,
        "documents": get_required_documents(),
        "tips": tips,
        "state_info": state_info,
    }


# ---------------------------------------------------------------------------
# Ballot Simulator
# ---------------------------------------------------------------------------

def get_evm_candidates() -> list[str]:
    """Return the default list of mock candidates for the EVM simulator.

    Returns:
        List of candidate labels (party — name).
    """
    return EVM_CANDIDATES_DEFAULT.copy()


def simulate_ballot(candidate_index: int, candidates: list[str]) -> dict:
    """Simulate the EVM voting and VVPAT verification process.

    Args:
        candidate_index: Zero-based index of the chosen candidate.
        candidates: List of candidate labels.

    Returns:
        Dict with keys:
            - success (bool): Whether the vote was recorded.
            - selected_candidate (str): The chosen candidate label.
            - vvpat_match (bool): Whether VVPAT matches EVM selection.
            - evm_explanation (str): Step-by-step EVM process.
            - vvpat_explanation (str): Step-by-step VVPAT process.
            - error (str | None): Error message if invalid.
    """
    if not candidates:
        return {
            "success": False,
            "selected_candidate": "",
            "vvpat_match": False,
            "evm_explanation": "",
            "vvpat_explanation": "",
            "error": "No candidates available.",
        }

    if candidate_index < 0 or candidate_index >= len(candidates):
        return {
            "success": False,
            "selected_candidate": "",
            "vvpat_match": False,
            "evm_explanation": "",
            "vvpat_explanation": "",
            "error": f"Invalid selection. Choose between 0 and {len(candidates) - 1}.",
        }

    selected: str = candidates[candidate_index]
    is_nota: bool = "NOTA" in selected.upper()

    evm_explanation: str = (
        "**How the EVM Records Your Vote:**\n\n"
        "1. The Presiding Officer activates the Ballot Unit for one vote.\n"
        "2. You press the **blue button** next to your chosen candidate.\n"
        "3. A **beep sounds** and a **red light glows** on the Control Unit — confirming your vote.\n"
        "4. The EVM stores the vote in its memory chip — no network transmission occurs.\n"
        "5. The machine locks until the next voter is authorized."
    )

    vvpat_explanation: str = (
        "**How VVPAT Confirms Your Vote:**\n\n"
        f"1. After you pressed the button, the VVPAT printer generated a slip showing:\n"
        f"   → **Candidate:** {selected}\n"
        f"   → **Party Symbol** next to the name.\n"
        "2. The slip was displayed behind a **transparent window for 7 seconds**.\n"
        "3. You visually verified that the printed name matches your choice.\n"
        "4. The slip then **dropped into a sealed VVPAT box** automatically.\n"
        "5. These slips are used for **random verification** during counting."
    )

    if is_nota:
        evm_explanation += (
            "\n\n> **NOTA Selected:** Your vote is recorded as 'None of the Above'. "
            "This officially registers your dissatisfaction but does not affect the "
            "winner determination."
        )

    return {
        "success": True,
        "selected_candidate": selected,
        "vvpat_match": True,  # In simulation, VVPAT always matches
        "evm_explanation": evm_explanation,
        "vvpat_explanation": vvpat_explanation,
        "error": None,
    }


# ---------------------------------------------------------------------------
# Myth Buster
# ---------------------------------------------------------------------------

def check_myth(claim: str) -> dict:
    """Verify an election-related claim against the curated myth database.

    Performs fuzzy matching against stored myths and returns the best match
    with its verdict, explanation, and source.

    Args:
        claim: The user's election-related claim or question.

    Returns:
        Dict with keys:
            - found (bool): Whether a matching myth was found.
            - myth (str): The matched myth statement.
            - verdict (str): TRUE / FALSE / PARTIALLY TRUE.
            - explanation (str): Detailed explanation.
            - source (str): Official source reference.
            - all_myths (list[dict]): Complete myth database for browsing.
    """
    claim = sanitize_input(claim)
    myths: list[dict[str, str]] = get_election_myths()

    if not claim:
        return {
            "found": False,
            "myth": "",
            "verdict": "",
            "explanation": "Please enter a claim to verify.",
            "source": "",
            "all_myths": myths,
        }

    claim_lower: str = claim.lower()
    claim_words: set[str] = set(claim_lower.split())

    best_match: Optional[dict[str, str]] = None
    best_score: int = 0

    for myth_entry in myths:
        myth_lower: str = myth_entry["myth"].lower()
        myth_words: set[str] = set(myth_lower.split())

        # Calculate word overlap score
        common: set[str] = claim_words & myth_words
        # Remove trivial words from scoring
        trivial: set[str] = {"the", "a", "an", "in", "is", "can", "be", "to", "of", "and", "or", "for", "not", "are", "you", "it", "that", "this"}
        meaningful_common: set[str] = common - trivial
        score: int = len(meaningful_common)

        # Also check substring match
        if claim_lower in myth_lower or myth_lower in claim_lower:
            score += 5

        # Check for key terms
        key_terms: list[str] = ["evm", "hack", "nota", "voter id", "vvpat", "nri", "online", "ink", "postal", "compulsory", "booth", "criminal"]
        for term in key_terms:
            if term in claim_lower and term in myth_lower:
                score += 3

        if score > best_score:
            best_score = score
            best_match = myth_entry

    if best_match and best_score >= 2:
        return {
            "found": True,
            "myth": best_match["myth"],
            "verdict": best_match["verdict"],
            "explanation": best_match["explanation"],
            "source": best_match["source"],
            "all_myths": myths,
        }

    return {
        "found": False,
        "myth": "",
        "verdict": "",
        "explanation": (
            "No exact match found in our database. Try rephrasing your question, "
            "or browse the common myths below."
        ),
        "source": "",
        "all_myths": myths,
    }


# ---------------------------------------------------------------------------
# Google Maps Integration
# ---------------------------------------------------------------------------

def get_polling_station_map_url(
    location: str = "India Gate, New Delhi",
    zoom: int = 15,
    size: str = "600x300",
) -> str:
    """Generate a Google Maps Static API URL for polling station visualization.

    Uses the GOOGLE_MAPS_API_KEY from environment variables. Falls back to
    a placeholder if the key is not set.

    Args:
        location: Address or landmark for the map center.
        zoom: Map zoom level (1-20).
        size: Image dimensions as 'WIDTHxHEIGHT'.

    Returns:
        URL string for the static map image.
    """
    api_key: str = os.getenv("GOOGLE_MAPS_API_KEY", "")
    encoded_location: str = urllib.parse.quote(location)

    if api_key:
        return (
            f"https://maps.googleapis.com/maps/api/staticmap"
            f"?center={encoded_location}"
            f"&zoom={zoom}"
            f"&size={size}"
            f"&markers=color:red%7C{encoded_location}"
            f"&key={api_key}"
        )

    # Fallback: OpenStreetMap embed (no API key needed)
    return (
        f"https://www.openstreetmap.org/export/embed.html"
        f"?bbox=77.1,28.5,77.3,28.7"
        f"&layer=mapnik"
        f"&marker=28.6139,77.2090"
    )


def get_map_fallback_message() -> str:
    """Return a user-friendly message when Maps API key is not configured.

    Returns:
        Informational string about the map placeholder.
    """
    api_key: str = os.getenv("GOOGLE_MAPS_API_KEY", "")
    if api_key:
        return ""
    return (
        "Showing a demo map of New Delhi. To see your actual nearest polling station, "
        "configure your `GOOGLE_MAPS_API_KEY` in the `.env` file."
    )
