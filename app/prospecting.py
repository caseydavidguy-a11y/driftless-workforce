"""Turn employer hiring observations into recruiting prospect intelligence."""

from __future__ import annotations

from dataclasses import dataclass
from .models import Employer


@dataclass(frozen=True)
class ProspectProfile:
    employer: str
    score: int
    priority: str
    hiring_summary: str
    reasons: tuple[str, ...]
    target_roles: tuple[str, ...]
    industries: tuple[str, ...]
    outreach_angle: str


def _role_family(title: str) -> str:
    value = title.lower()
    if any(k in value for k in ("manager", "supervisor", "director", "lead", "chief")):
        return "leadership"
    if any(k in value for k in ("maintenance", "technician", "mechanic", "lineworker", "electrician", "hvac")):
        return "skilled trades / maintenance"
    if any(k in value for k in ("warehouse", "shipping", "receiving", "material", "inventory", "stock", "freight")):
        return "warehouse / materials"
    if any(k in value for k in ("production", "operator", "manufacturing", "fabrication", "quality")):
        return "manufacturing / production"
    if any(k in value for k in ("restaurant", "cook", "food", "barista", "crew", "server", "hospitality")):
        return "hospitality / food service"
    return "general operations"


def build_prospect(employer: Employer) -> ProspectProfile:
    observations = employer.observations
    role_families = sorted({_role_family(o.title) for o in observations})
    manager_roles = [o.title for o in observations if any(k in o.title.lower() for k in ("manager", "supervisor", "director", "lead", "chief"))]

    reasons: list[str] = []
    if employer.opening_count >= 5:
        reasons.append(f"{employer.opening_count} observed openings indicate meaningful hiring volume")
    elif employer.opening_count >= 2:
        reasons.append(f"{employer.opening_count} observed openings indicate active hiring")
    if len(employer.locations) > 1:
        reasons.append("Hiring activity spans multiple local locations")
    if employer.industries:
        reasons.append("Hiring overlaps Driftless Workforce target industries")
    if manager_roles:
        reasons.append(f"Leadership hiring signal: {', '.join(manager_roles[:3])}")
    if not reasons:
        reasons.append("A verified local opening creates a recruiting conversation opportunity")

    if employer.opening_count >= 5 or len(manager_roles) >= 2:
        angle = "Lead with capacity: ask whether the current hiring volume is creating bottlenecks and offer targeted recruiting support for the roles already being advertised."
    elif manager_roles:
        angle = "Lead with leadership recruiting: reference the visible management hiring signal and offer help building a qualified local leadership pipeline."
    else:
        angle = "Lead with the specific hard-to-fill role and offer a focused candidate-sourcing conversation rather than a generic staffing pitch."

    summary = f"{employer.name} has {employer.opening_count} observed opening(s) across {len(employer.locations) or 1} local location(s)."
    return ProspectProfile(
        employer=employer.name,
        score=employer.score,
        priority=employer.priority,
        hiring_summary=summary,
        reasons=tuple(reasons),
        target_roles=tuple(role_families),
        industries=tuple(sorted(employer.industries)),
        outreach_angle=angle,
    )


def build_prospect_list(employers: list[Employer]) -> list[ProspectProfile]:
    """Return outreach-ready prospects in score order."""
    return [build_prospect(e) for e in sorted(employers, key=lambda x: (-x.score, x.canonical_name))]
