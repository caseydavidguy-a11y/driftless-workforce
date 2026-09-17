"""Prospect scouting layer for the Driftless AI sales pipeline.

Scout consumes existing Employer objects and turns them into normalized,
explainable prospect candidates. It deliberately does not discover or send
contact information; that belongs to Hunter and Outreach.
"""

from dataclasses import asdict, dataclass
from typing import Iterable

from .models import Employer


@dataclass(frozen=True)
class ProspectCandidate:
    employer: str
    canonical_name: str
    locations: tuple[str, ...]
    industries: tuple[str, ...]
    opening_count: int
    verified_opening_count: int
    score: int
    priority: str
    reasons: tuple[str, ...]

    @property
    def key(self) -> str:
        return self.canonical_name


def _reasons(employer: Employer) -> tuple[str, ...]:
    reasons: list[str] = []
    if employer.verified_opening_count:
        reasons.append(f"{employer.verified_opening_count} verified opening(s)")
    if employer.opening_count > 1:
        reasons.append(f"{employer.opening_count} active openings")
    if employer.priority in {"Pursue", "High"}:
        reasons.append(f"opportunity priority: {employer.priority}")
    if employer.industries:
        reasons.append("target industry: " + ", ".join(sorted(employer.industries)))
    return tuple(reasons)


def build_prospect_queue(
    employers: Iterable[Employer],
    *,
    minimum_score: int = 0,
    priorities: set[str] | None = None,
    limit: int | None = None,
) -> list[ProspectCandidate]:
    """Build a deterministic prospect queue from existing employer intelligence."""
    allowed_priorities = priorities or {"Pursue", "Monitor", "High", "Medium", "Low"}
    candidates = [
        ProspectCandidate(
            employer=e.name,
            canonical_name=e.canonical_name,
            locations=tuple(sorted(e.locations)),
            industries=tuple(sorted(e.industries)),
            opening_count=e.opening_count,
            verified_opening_count=e.verified_opening_count,
            score=e.score,
            priority=e.priority,
            reasons=_reasons(e),
        )
        for e in employers
        if e.score >= minimum_score and e.priority in allowed_priorities
    ]
    candidates.sort(key=lambda p: (-p.score, -p.verified_opening_count, -p.opening_count, p.canonical_name))
    return candidates[:limit] if limit is not None else candidates


def prospect_to_dict(prospect: ProspectCandidate) -> dict:
    """Return a JSON-friendly representation for API/frontend consumers."""
    return asdict(prospect)
