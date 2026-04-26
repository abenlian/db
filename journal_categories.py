"""
Journal / venue classification for academic ranking lists.

Supported lists
---------------
FT50     : Financial Times Top 50 journals (business school research)
UTD24    : UT Dallas 24 journals (management research)
BASKET8  : AIS Senior Scholars' Basket of 8 IS journals
VHB_A    : VHB-JOURQUAL 3 rating A or A+ (German Academic Association)
VHB_Aplus: VHB-JOURQUAL 3 rating A+ only

Each journal is stored under the canonical name used most often in
Google Scholar / publication lists.  Matching is done
case-insensitively against a broad set of aliases.
"""

from __future__ import annotations
import re

# ── canonical name → {list: True} ────────────────────────────────────────────

JOURNALS: dict[str, dict[str, bool]] = {
    # ── MIS Quarterly ─────────────────────────────────────────────────────────
    "MIS Quarterly": {
        "FT50": True, "UTD24": True, "BASKET8": True,
        "VHB_A": True, "VHB_Aplus": True,
    },
    # ── Information Systems Research ──────────────────────────────────────────
    "Information Systems Research": {
        "FT50": True, "UTD24": True, "BASKET8": True,
        "VHB_A": True, "VHB_Aplus": True,
    },
    # ── Journal of Management Information Systems ─────────────────────────────
    "Journal of Management Information Systems": {
        "FT50": True, "UTD24": True, "BASKET8": True,
        "VHB_A": True, "VHB_Aplus": False,
    },
    # ── Journal of Information Technology ────────────────────────────────────
    "Journal of Information Technology": {
        "FT50": False, "UTD24": False, "BASKET8": True,
        "VHB_A": True, "VHB_Aplus": False,
    },
    # ── European Journal of Information Systems ───────────────────────────────
    "European Journal of Information Systems": {
        "FT50": False, "UTD24": False, "BASKET8": True,
        "VHB_A": True, "VHB_Aplus": False,
    },
    # ── Information Systems Journal ───────────────────────────────────────────
    "Information Systems Journal": {
        "FT50": False, "UTD24": False, "BASKET8": True,
        "VHB_A": True, "VHB_Aplus": False,
    },
    # ── Journal of the Association for Information Systems ────────────────────
    "Journal of the Association for Information Systems": {
        "FT50": False, "UTD24": False, "BASKET8": True,
        "VHB_A": True, "VHB_Aplus": False,
    },
    # ── Journal of Strategic Information Systems ──────────────────────────────
    "Journal of Strategic Information Systems": {
        "FT50": False, "UTD24": False, "BASKET8": True,
        "VHB_A": True, "VHB_Aplus": False,
    },
    # ── Business & Information Systems Engineering ────────────────────────────
    "Business & Information Systems Engineering": {
        "FT50": False, "UTD24": False, "BASKET8": False,
        "VHB_A": True, "VHB_Aplus": False,
    },
    # ── Management Science ─────────────────────────────────────────────────────
    "Management Science": {
        "FT50": True, "UTD24": True, "BASKET8": False,
        "VHB_A": True, "VHB_Aplus": True,
    },
    # ── Organization Science ──────────────────────────────────────────────────
    "Organization Science": {
        "FT50": True, "UTD24": True, "BASKET8": False,
        "VHB_A": True, "VHB_Aplus": False,
    },
    # ── Journal of Marketing Research ─────────────────────────────────────────
    "Journal of Marketing Research": {
        "FT50": True, "UTD24": True, "BASKET8": False,
        "VHB_A": True, "VHB_Aplus": True,
    },
    # ── Strategic Management Journal ──────────────────────────────────────────
    "Strategic Management Journal": {
        "FT50": True, "UTD24": True, "BASKET8": False,
        "VHB_A": True, "VHB_Aplus": True,
    },
    # ── Information & Management ──────────────────────────────────────────────
    "Information & Management": {
        "FT50": False, "UTD24": False, "BASKET8": False,
        "VHB_A": False, "VHB_Aplus": False,
    },
    # ── Decision Support Systems ──────────────────────────────────────────────
    "Decision Support Systems": {
        "FT50": False, "UTD24": False, "BASKET8": False,
        "VHB_A": False, "VHB_Aplus": False,
    },
    # ── Electronic Markets ────────────────────────────────────────────────────
    "Electronic Markets": {
        "FT50": False, "UTD24": False, "BASKET8": False,
        "VHB_A": False, "VHB_Aplus": False,
    },
    # ── Journal of Computer-Mediated Communication ────────────────────────────
    "Journal of Computer-Mediated Communication": {
        "FT50": False, "UTD24": False, "BASKET8": False,
        "VHB_A": False, "VHB_Aplus": False,
    },
    # ── MIS Quarterly Executive ───────────────────────────────────────────────
    "MIS Quarterly Executive": {
        "FT50": False, "UTD24": False, "BASKET8": False,
        "VHB_A": False, "VHB_Aplus": False,
    },
    # ── Entrepreneurship Theory and Practice ──────────────────────────────────
    "Entrepreneurship Theory and Practice": {
        "FT50": True, "UTD24": False, "BASKET8": False,
        "VHB_A": True, "VHB_Aplus": False,
    },
    # ── Journal of Service Research ───────────────────────────────────────────
    "Journal of Service Research": {
        "FT50": True, "UTD24": False, "BASKET8": False,
        "VHB_A": True, "VHB_Aplus": False,
    },
    # ── Journal of Marketing ──────────────────────────────────────────────────
    "Journal of Marketing": {
        "FT50": True, "UTD24": True, "BASKET8": False,
        "VHB_A": True, "VHB_Aplus": True,
    },
    # ── Academy of Management Review ─────────────────────────────────────────
    "Academy of Management Review": {
        "FT50": True, "UTD24": True, "BASKET8": False,
        "VHB_A": True, "VHB_Aplus": True,
    },
    # ── International Journal of Electronic Commerce ───────────────────────────
    "International Journal of Electronic Commerce": {
        "FT50": False, "UTD24": False, "BASKET8": False,
        "VHB_A": False, "VHB_Aplus": False,
    },
    # ── Electronic Commerce Research and Applications ─────────────────────────
    "Electronic Commerce Research and Applications": {
        "FT50": False, "UTD24": False, "BASKET8": False,
        "VHB_A": False, "VHB_Aplus": False,
    },
    # ── Journal of Interactive Marketing ──────────────────────────────────────
    "Journal of Interactive Marketing": {
        "FT50": False, "UTD24": False, "BASKET8": False,
        "VHB_A": False, "VHB_Aplus": False,
    },
    # ── European Journal of Operational Research ──────────────────────────────
    "European Journal of Operational Research": {
        "FT50": True, "UTD24": False, "BASKET8": False,
        "VHB_A": True, "VHB_Aplus": False,
    },
    # ── HMD Praxis der Wirtschaftsinformatik ──────────────────────────────────
    "HMD Praxis der Wirtschaftsinformatik": {
        "FT50": False, "UTD24": False, "BASKET8": False,
        "VHB_A": False, "VHB_Aplus": False,
    },
}

# ── aliases → canonical name ──────────────────────────────────────────────────
# Keys are lowercased for matching.

ALIASES: dict[str, str] = {
    # MIS Quarterly
    "mis quarterly": "MIS Quarterly",
    "misq": "MIS Quarterly",
    "management information systems quarterly": "MIS Quarterly",
    # Information Systems Research
    "information systems research": "Information Systems Research",
    "isr": "Information Systems Research",
    # JMIS
    "journal of management information systems": "Journal of Management Information Systems",
    "jmis": "Journal of Management Information Systems",
    # JIT
    "journal of information technology": "Journal of Information Technology",
    "jit": "Journal of Information Technology",
    # EJIS
    "european journal of information systems": "European Journal of Information Systems",
    "ejis": "European Journal of Information Systems",
    # ISJ
    "information systems journal": "Information Systems Journal",
    "isj": "Information Systems Journal",
    # JAIS
    "journal of the association for information systems": "Journal of the Association for Information Systems",
    "jais": "Journal of the Association for Information Systems",
    "journal of association for information systems": "Journal of the Association for Information Systems",
    # JSIS
    "journal of strategic information systems": "Journal of Strategic Information Systems",
    "jsis": "Journal of Strategic Information Systems",
    # BISE
    "business & information systems engineering": "Business & Information Systems Engineering",
    "business and information systems engineering": "Business & Information Systems Engineering",
    "bise": "Business & Information Systems Engineering",
    "wirtschaftsinformatik": "Business & Information Systems Engineering",
    # Management Science
    "management science": "Management Science",
    # Organization Science
    "organization science": "Organization Science",
    # Marketing journals
    "journal of marketing research": "Journal of Marketing Research",
    "jmr": "Journal of Marketing Research",
    # Strategy
    "strategic management journal": "Strategic Management Journal",
    "smj": "Strategic Management Journal",
    # Lower-tier IS
    "information & management": "Information & Management",
    "information and management": "Information & Management",
    "i&m": "Information & Management",
    "decision support systems": "Decision Support Systems",
    "dss": "Decision Support Systems",
    "electronic markets": "Electronic Markets",
    "journal of computer-mediated communication": "Journal of Computer-Mediated Communication",
    "journal of computer mediated communication": "Journal of Computer-Mediated Communication",
    "jcmc": "Journal of Computer-Mediated Communication",
    "mis quarterly executive": "MIS Quarterly Executive",
    "misq executive": "MIS Quarterly Executive",
    # Entrepreneurship
    "entrepreneurship theory and practice": "Entrepreneurship Theory and Practice",
    "etp": "Entrepreneurship Theory and Practice",
    # Service research
    "journal of service research": "Journal of Service Research",
    "jsr": "Journal of Service Research",
    # Marketing
    "journal of marketing": "Journal of Marketing",
    "journal of marketing research": "Journal of Marketing Research",
    "journal of interactive marketing": "Journal of Interactive Marketing",
    # Operations research
    "european journal of operational research": "European Journal of Operational Research",
    "ejor": "European Journal of Operational Research",
    # E-commerce
    "international journal of electronic commerce": "International Journal of Electronic Commerce",
    "ijec": "International Journal of Electronic Commerce",
    "electronic commerce research and applications": "Electronic Commerce Research and Applications",
    "ecra": "Electronic Commerce Research and Applications",
    # German IS outlet
    "hmd praxis der wirtschaftsinformatik": "HMD Praxis der Wirtschaftsinformatik",
    "hmd": "HMD Praxis der Wirtschaftsinformatik",
    "wirtschaftsinformatik": "Business & Information Systems Engineering",
    "wi": "Business & Information Systems Engineering",
}

ALL_LISTS = ["FT50", "UTD24", "BASKET8", "VHB_A", "VHB_Aplus"]

LIST_LABELS = {
    "FT50":     "FT 50",
    "UTD24":    "UTD 24",
    "BASKET8":  "AIS Basket of 8",
    "VHB_A":    "VHB A / A+",
    "VHB_Aplus":"VHB A+",
}

LIST_COLORS = {
    "FT50":     "#2563EB",   # blue
    "UTD24":    "#7C3AED",   # violet
    "BASKET8":  "#0D9488",   # teal
    "VHB_A":    "#D97706",   # amber
    "VHB_Aplus":"#DC2626",   # red
    "None":     "#CBD5E1",   # slate (not in any list)
}


def _normalize(text: str) -> str:
    """Lowercase, collapse whitespace, strip punctuation variants."""
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text


def canonical(venue: str) -> str | None:
    """Return the canonical journal name for *venue*, or None if unknown."""
    if not venue:
        return None
    key = _normalize(venue)
    if key in ALIASES:
        return ALIASES[key]
    # partial match on canonical names
    for alias, canon in ALIASES.items():
        if alias in key or key in alias:
            return canon
    return None


def classify(venue: str) -> dict[str, bool]:
    """Return {list_name: bool} membership for *venue*."""
    canon = canonical(venue)
    if canon and canon in JOURNALS:
        return JOURNALS[canon]
    return {lst: False for lst in ALL_LISTS}


def best_list(venue: str) -> str:
    """Return the most prestigious list the venue belongs to, or 'Other'."""
    membership = classify(venue)
    for lst in ["VHB_Aplus", "FT50", "UTD24", "BASKET8", "VHB_A"]:
        if membership.get(lst):
            return lst
    return "None"


def get_canonical_name(venue: str) -> str:
    """Return canonical name or the original venue string."""
    return canonical(venue) or venue
