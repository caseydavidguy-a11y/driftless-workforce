"""Decision-maker enrichment primitives for the Driftless recruiting pipeline.

Hunter deliberately accepts verified contact records rather than guessing contact
details. External discovery adapters can feed this module later.
"""
from dataclasses import asdict, dataclass
from typing import Iterable


@dataclass(frozen=True)
class VerifiedContact:
    employer_slug: str
    name: str
    title: str
    source_url: str
    verified_at: str
    email: str | None = None
    phone: str | None = None


ROLE_PRIORITY = (
    "talent acquisition",
    "recruiting",
    "human resources",
    "hr",
    "operations",
    "general manager",
    "owner",
)


def rank_contacts(contacts: Iterable[VerifiedContact]) -> list[VerifiedContact]:
    """Rank verified contacts by relevance without fabricating missing data."""
    def rank(contact: VerifiedContact) -> tuple[int, str, str]:
        title = contact.title.lower()
        score = next((len(ROLE_PRIORITY) - i for i, role in enumerate(ROLE_PRIORITY) if role in title), 0)
        return (-score, title, contact.name.lower())

    return sorted(contacts, key=rank)


def hunter_record(prospect: dict, contacts: Iterable[VerifiedContact]) -> dict:
    """Attach verified contacts to a prospect and preserve source evidence."""
    matches = [
        c for c in rank_contacts(contacts)
        if c.employer_slug == prospect.get("slug")
    ]
    return {
        **prospect,
        "contact": asdict(matches[0]) if matches else None,
        "contact_candidates": [asdict(c) for c in matches],
        "hunter_status": "verified" if matches else "needs_research",
    }
