"""Build safe, public-contact research targets for recruiting prospects."""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import quote_plus

from .prospecting import ProspectProfile


@dataclass(frozen=True)
class ContactTarget:
    employer: str
    role: str
    priority: int
    reason: str
    search_queries: tuple[str, ...]
    public_contact_paths: tuple[str, ...]


def _roles_for(prospect: ProspectProfile) -> list[tuple[str, int, str]]:
    roles: list[tuple[str, int, str]] = []
    if "leadership" in prospect.target_roles:
        roles.append(("HR / Talent Acquisition leader", 100, "Leadership hiring creates a direct recruiting signal."))
    if any("manufacturing" in r for r in prospect.target_roles):
        roles.append(("Plant / Operations leader", 92, "Manufacturing hiring is often owned or strongly influenced by operations leadership."))
    if any("warehouse" in r for r in prospect.target_roles):
        roles.append(("Warehouse / Distribution leader", 88, "Warehouse and materials hiring points toward the local operations owner."))
    if any("trades" in r for r in prospect.target_roles):
        roles.append(("Maintenance / Engineering leader", 86, "Skilled-trades hiring often routes through maintenance or engineering leadership."))
    roles.append(("HR / Recruiting contact", 80, "General recruiting contact is the safest fallback when an exact hiring owner is unknown."))
    return roles


def build_contact_targets(prospect: ProspectProfile) -> list[ContactTarget]:
    """Return research targets without inventing names, emails, or phone numbers."""
    targets: list[ContactTarget] = []
    for role, priority, reason in _roles_for(prospect):
        queries = (
            f'"{prospect.employer}" "{role}"',
            f'"{prospect.employer}" HR recruiting',
            f'"{prospect.employer}" careers contact',
        )
        encoded_employer = quote_plus(prospect.employer)
        paths = (
            "Employer website / careers page",
            "Employer LinkedIn company page",
            f"Search engine query: {encoded_employer}",
        )
        targets.append(ContactTarget(
            employer=prospect.employer,
            role=role,
            priority=priority,
            reason=reason,
            search_queries=queries,
            public_contact_paths=paths,
        ))
    # Deduplicate role targets while preserving priority order.
    return sorted({(t.role, t): t for t in targets}.values(), key=lambda t: -t.priority)
