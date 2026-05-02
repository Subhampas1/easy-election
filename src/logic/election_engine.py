"""
election_engine.py — Core Election Business Logic

Contains all business logic for roadmap generation, ballot simulation,
myth verification, and election data management.
"""

import re
from typing import Optional
from dataclasses import dataclass, field

import streamlit as st

from src.utils.validators import sanitize_input
from src.services.cloud_logging_service import get_logger, log_user_action


@dataclass
class RoadmapResult:
    """Result of a personalized election roadmap generation."""
    eligible: bool
    title: str
    steps: list[dict[str, str | int]]
    documents: dict[str, list[str]]
    tips: list[str]
    state_info: Optional[dict[str, str]]


@dataclass
class BallotResult:
    """Result of an EVM ballot simulation."""
    success: bool
    selected_candidate: str
    vvpat_match: bool
    evm_explanation: str
    vvpat_explanation: str
    error: Optional[str]


@dataclass
class MythCheckResult:
    """Result of an election myth verification."""
    found: bool
    myth: str
    verdict: str
    explanation: str
    source: str
    all_myths: list[dict[str, str]] = field(default_factory=list)


INDIAN_STATES: list[str] = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar",
    "Chhattisgarh", "Goa", "Gujarat", "Haryana", "Himachal Pradesh",
    "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra",
    "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab",
    "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura",
    "Uttar Pradesh", "Uttarakhand", "West Bengal",
    "Andaman & Nicobar Islands", "Chandigarh",
    "Dadra & Nagar Haveli and Daman & Diu",
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
    """Return the sorted list of Indian states and union territories."""
    return sorted(INDIAN_STATES)


@st.cache_data
def get_required_documents() -> dict[str, list[str]]:
    """Return documents required for voter registration."""
    return {
        "Identity Proof (any one)": [
            "Aadhaar Card", "PAN Card", "Driving License",
            "Passport", "Bank Passbook with Photo", "Government-issued Photo ID",
        ],
        "Address Proof (any one)": [
            "Aadhaar Card", "Utility Bill (electricity, water, gas)",
            "Bank Statement / Passbook", "Rent Agreement",
            "Ration Card", "Government-issued Address Proof",
        ],
        "Age Proof (any one)": [
            "Birth Certificate", "School Leaving Certificate / Marksheet",
            "Aadhaar Card", "PAN Card", "Passport",
        ],
        "Photographs": ["2 recent passport-size colour photographs"],
    }


@st.cache_data
def get_election_myths() -> list[dict[str, str]]:
    """Return curated list of common election myths with verdicts."""
    return [
        {"myth": "EVMs can be hacked remotely", "verdict": "FALSE",
         "explanation": "EVMs are standalone devices with no wireless connectivity, Wi-Fi, Bluetooth, or internet connection. They use one-time programmable chips that cannot be reprogrammed once manufactured. The Election Commission conducts rigorous testing including first-level checking (FLC) before every election.",
         "source": "Election Commission of India — EVM FAQ"},
        {"myth": "You need a Voter ID card to vote", "verdict": "PARTIALLY TRUE",
         "explanation": "While the EPIC (Voter ID) is the primary document, the ECI accepts 12 alternative photo IDs including Aadhaar, Passport, Driving License, PAN Card, and others. Your name must be on the electoral roll regardless of which ID you carry.",
         "source": "ECI Order — Alternative Photo IDs for Voting"},
        {"myth": "NOTA vote can defeat a candidate", "verdict": "FALSE",
         "explanation": "Even if NOTA receives the highest number of votes, the candidate with the most votes among the contesting candidates wins. NOTA is counted but does not affect the result.",
         "source": "Supreme Court Judgment — PUCL vs Union of India (2013)"},
        {"myth": "Voting is compulsory in India", "verdict": "FALSE",
         "explanation": "Voting is a constitutional right but not a legal obligation in India at the national level. Some states like Gujarat have enacted laws making voting compulsory for local body elections.",
         "source": "Article 326, Constitution of India"},
        {"myth": "You can vote from any polling station", "verdict": "FALSE",
         "explanation": "You can only vote at the specific polling station assigned to your address on the electoral roll. Check your assigned station on the NVSP portal or Voter Helpline app.",
         "source": "Section 62, Representation of the People Act 1951"},
        {"myth": "Postal ballots are only for military personnel", "verdict": "FALSE",
         "explanation": "Postal ballots are available for service voters, government employees on election duty, voters above 80, persons with disabilities, and voters under preventive detention.",
         "source": "ECI Guidelines on Postal Ballot"},
        {"myth": "NRIs cannot vote in Indian elections", "verdict": "FALSE",
         "explanation": "NRIs can register as overseas electors under Section 20A of the RP Act 1950 (amended in 2010). They must be present in their constituency on polling day to vote in person.",
         "source": "Section 20A, Representation of the People Act 1950"},
        {"myth": "The VVPAT slip can be taken home as proof", "verdict": "FALSE",
         "explanation": "The VVPAT slip is displayed behind a glass window for 7 seconds and then drops into a sealed box. Voters are NOT allowed to touch, photograph, or take the slip.",
         "source": "Rule 49MA, Conduct of Election Rules 1961"},
        {"myth": "Candidates with criminal cases cannot contest elections", "verdict": "FALSE",
         "explanation": "Only candidates CONVICTED and sentenced to 2+ years imprisonment are disqualified. Candidates with pending criminal cases can still contest elections.",
         "source": "Section 8, Representation of the People Act 1951"},
        {"myth": "Election results can be challenged only by candidates", "verdict": "FALSE",
         "explanation": "Any elector can file an election petition challenging results within 45 days of the result declaration before the High Court.",
         "source": "Section 81, Representation of the People Act 1951"},
        {"myth": "You must vote for a party, not a candidate", "verdict": "FALSE",
         "explanation": "In Indian elections, you vote for a CANDIDATE, not a party. Independent candidates also contest without any party affiliation.",
         "source": "Election Commission of India — Voter Education"},
        {"myth": "Booth capturing still happens in modern elections", "verdict": "PARTIALLY TRUE",
         "explanation": "While booth capturing has drastically reduced due to EVMs, CCTV surveillance, webcasting, and micro-observers, isolated incidents still occur in some regions.",
         "source": "Section 135A, Representation of the People Act 1951"},
        {"myth": "The Election Commission can postpone elections indefinitely", "verdict": "FALSE",
         "explanation": "The ECI must conduct elections within the time frame specified by the Constitution. A new Lok Sabha must be constituted before the expiry of the current one (5 years).",
         "source": "Article 83 & 172, Constitution of India"},
        {"myth": "Ink on the finger wears off in a few hours", "verdict": "FALSE",
         "explanation": "The indelible ink contains silver nitrate and lasts 2-4 weeks. It is applied on the left index finger's nail and cuticle to prevent double voting.",
         "source": "Mysore Paints & Varnish Ltd. — ECI Ink Specification"},
        {"myth": "You can vote online in Indian elections", "verdict": "FALSE",
         "explanation": "India does not have an internet/online voting system for general or state elections. All voting is done in person at polling stations or via postal ballot for eligible categories.",
         "source": "Election Commission of India — Official FAQ"},
    ]


@st.cache_data
def get_state_specific_info() -> dict[str, dict[str, str]]:
    """Return state-specific election details."""
    return {
        "Delhi": {"chief_electoral_officer": "CEO Delhi Office", "helpline": "1950", "website": "https://ceodelhi.gov.in", "note": "Delhi has a separate State Election Commission for MCD elections."},
        "Maharashtra": {"chief_electoral_officer": "CEO Maharashtra Office", "helpline": "1950", "website": "https://ceo.maharashtra.gov.in", "note": "Maharashtra uses online Form 6 for new registrations via NVSP."},
        "Tamil Nadu": {"chief_electoral_officer": "CEO Tamil Nadu Office", "helpline": "1950", "website": "https://elections.tn.gov.in", "note": "Tamil Nadu provides voter slips in both Tamil and English."},
        "Uttar Pradesh": {"chief_electoral_officer": "CEO UP Office", "helpline": "1950", "website": "https://ceouttarpradesh.nic.in", "note": "UP, being the largest state, has elections in multiple phases."},
        "Karnataka": {"chief_electoral_officer": "CEO Karnataka Office", "helpline": "1950", "website": "https://ceo.karnataka.gov.in", "note": "Karnataka pioneered webcasting of polling stations."},
    }


def generate_roadmap(state: str, age: int) -> dict:
    """Generate a personalized election-readiness roadmap.

    Args:
        state: The Indian state/UT the user resides in.
        age: The user's current age in years.

    Returns:
        Dict with eligible, title, steps, documents, tips, state_info.
    """
    state = sanitize_input(state)
    eligible: bool = age >= 18
    state_info: Optional[dict] = get_state_specific_info().get(state)
    log_user_action("roadmap_generated", {"state": state, "age": age, "eligible": eligible})

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

    return {"eligible": True, "title": f"Your Election Roadmap — {state}", "steps": steps, "documents": get_required_documents(), "tips": tips, "state_info": state_info}


def get_evm_candidates() -> list[str]:
    """Return the default list of mock candidates for the EVM simulator."""
    return EVM_CANDIDATES_DEFAULT.copy()


def simulate_ballot(candidate_index: int, candidates: list[str]) -> dict:
    """Simulate the EVM voting and VVPAT verification process.

    Args:
        candidate_index: Zero-based index of the chosen candidate.
        candidates: List of candidate labels.

    Returns:
        Dict with success, selected_candidate, vvpat_match, explanations, error.
    """
    if not candidates:
        return {"success": False, "selected_candidate": "", "vvpat_match": False, "evm_explanation": "", "vvpat_explanation": "", "error": "No candidates available."}
    if candidate_index < 0 or candidate_index >= len(candidates):
        return {"success": False, "selected_candidate": "", "vvpat_match": False, "evm_explanation": "", "vvpat_explanation": "", "error": f"Invalid selection. Choose between 0 and {len(candidates) - 1}."}

    selected: str = candidates[candidate_index]
    is_nota: bool = "NOTA" in selected.upper()
    log_user_action("vote_cast", {"candidate": selected, "is_nota": is_nota})

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
        evm_explanation += "\n\n> **NOTA Selected:** Your vote is recorded as 'None of the Above'. This officially registers your dissatisfaction but does not affect the winner determination."

    return {"success": True, "selected_candidate": selected, "vvpat_match": True, "evm_explanation": evm_explanation, "vvpat_explanation": vvpat_explanation, "error": None}


def check_myth(claim: str) -> dict:
    """Verify an election-related claim against the curated myth database.

    Args:
        claim: The user's election-related claim or question.

    Returns:
        Dict with found, myth, verdict, explanation, source, all_myths.
    """
    claim = sanitize_input(claim)
    myths: list[dict[str, str]] = get_election_myths()
    if not claim:
        return {"found": False, "myth": "", "verdict": "", "explanation": "Please enter a claim to verify.", "source": "", "all_myths": myths}

    log_user_action("myth_check", {"claim": claim})
    claim_lower: str = claim.lower()
    claim_words: set[str] = set(claim_lower.split())
    best_match: Optional[dict[str, str]] = None
    best_score: int = 0
    trivial: set[str] = {"the", "a", "an", "in", "is", "can", "be", "to", "of", "and", "or", "for", "not", "are", "you", "it", "that", "this"}

    for myth_entry in myths:
        myth_lower: str = myth_entry["myth"].lower()
        myth_words: set[str] = set(myth_lower.split())
        common: set[str] = claim_words & myth_words
        meaningful_common: set[str] = common - trivial
        score: int = len(meaningful_common)
        if claim_lower in myth_lower or myth_lower in claim_lower:
            score += 5
        key_terms: list[str] = ["evm", "hack", "nota", "voter id", "vvpat", "nri", "online", "ink", "postal", "compulsory", "booth", "criminal"]
        for term in key_terms:
            if term in claim_lower and term in myth_lower:
                score += 3
        if score > best_score:
            best_score = score
            best_match = myth_entry

    if best_match and best_score >= 2:
        return {"found": True, "myth": best_match["myth"], "verdict": best_match["verdict"], "explanation": best_match["explanation"], "source": best_match["source"], "all_myths": myths}

    return {"found": False, "myth": "", "verdict": "", "explanation": "No exact match found in our database. Try rephrasing your question, or browse the common myths below.", "source": "", "all_myths": myths}
