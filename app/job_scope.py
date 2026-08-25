"""Hard job-scope rules for the Driftless Workforce Command Center."""
from __future__ import annotations
import re

FOCUSED_INDUSTRIES = {
    "manufacturing",
    "warehouse",
    "operations",
    "skilled trades",
    "hospitality",
    "leadership",
}

EXCLUDED_TITLE_PATTERNS = (
    r"\bteacher\b", r"\bteaching\b", r"\beducator\b", r"\bprofessor\b",
    r"\bcashier\b", r"\bretail associate\b", r"\bsales associate\b",
    r"\bstore associate\b", r"\bcrew member\b", r"\bbarista\b",
    r"\bserver\b", r"\bwaiter\b", r"\bwaitress\b",
    r"\bnurse\b", r"\bregistered nurse\b", r"\bphlebotom\w*\b",
)


def is_in_scope(title: str, industry: str) -> bool:
    """Return True only for focused industries and non-excluded roles."""
    normalized_industry = (industry or "").strip().lower()
    if normalized_industry not in FOCUSED_INDUSTRIES:
        return False
    normalized_title = re.sub(r"\s+", " ", (title or "").strip().lower())
    return not any(re.search(pattern, normalized_title) for pattern in EXCLUDED_TITLE_PATTERNS)


def filter_in_scope(observations):
    return [
        observation
        for observation in observations
        if is_in_scope(observation.title, observation.industry)
    ]
