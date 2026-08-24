"""Turn employer hiring observations into actionable recruiting prospects."""

from __future__ import annotations

from dataclasses import asdict, dataclass

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
    decision_maker_roles: tuple[str, ...]
    contact_path: str
    outreach_angle: str
    evidence: tuple[str, ...]


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


def _decision_maker_roles(employer: Employer) -> tuple[str, ...]:
    titles = " ".join(o.title.lower() for o in employer.observations)
    if any(k in titles for k in ("manager", "supervisor", "director", "lead", "chief")):
        return ("HR / Talent Acquisition", "Hiring Manager", "Operations Leader")
    return ("HR / Talent Acquisition", "Department Manager")


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
    if employer.verified_opening_count:
        reasons.append(f"{employer.verified_opening_count} opening(s) are source-verified")
    if employer.industries:
        reasons.append("Hiring overlaps Driftless Workforce target industries")
    if manager_roles:
        reasons.append(f"Leadership hiring signal: {', '.join(manager_roles[:3])}")
    if not reasons:
        reasons.append("A local opening creates a recruiting conversation opportunity")

    if employer.opening_count >= 5 or len(manager_roles) >= 2:
        angle = "Lead with capacity: ask whether current hiring volume is creating bottlenecks and offer targeted recruiting support for roles already being advertised."
    elif manager_roles:
        angle = "Lead with leadership recruiting: reference the visible management hiring signal and offer help building a qualified local leadership pipeline."
    else:
        angle = "Lead with the specific hard-to-fill role and offer a focused candidate-sourcing conversation rather than a generic staffing pitch."

    evidence = tuple(
        f"{o.title} — {o.location}" + (f" [{o.source}]" if o.source else "")
        for o in observations[:8]
    )

    return ProspectProfile(
        employer=employer.name,
        score=employer.score,
        priority=employer.priority,
        hiring_summary=f"{employer.name} has {employer.opening_count} observed opening(s) across {len(employer.locations) or 1} local location(s).",
        reasons=tuple(reasons),
        target_roles=tuple(role_families),
        industries=tuple(sorted(employer.industries)),
        decision_maker_roles=_decision_maker_roles(employer),
        contact_path="Find HR/Talent Acquisition or the hiring manager through the employer's official site or public professional profile. Do not guess an email address.",
        outreach_angle=angle,
        evidence=evidence,
    )


def build_prospect_list(employers: list[Employer]) -> list[ProspectProfile]:
    """Return outreach-ready prospects in score order."""
    return [build_prospect(e) for e in sorted(employers, key=lambda x: (-x.score, x.canonical_name))]


def prospect_to_dict(prospect: ProspectProfile) -> dict:
    """Serialize a prospect without inventing personal contact information."""
    return asdict(prospect)
