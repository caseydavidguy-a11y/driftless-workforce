"""Generate safe public-contact discovery targets.

This module does not scrape private data or infer personal contact details.
It produces focused search targets that can be resolved against public sources.
"""
from dataclasses import dataclass
from urllib.parse import quote_plus

@dataclass(frozen=True)
class DiscoveryTarget:
    employer: str
    role: str
    query: str
    rationale: str


def build_discovery_targets(employer: str, decision_maker_roles: tuple[str, ...]) -> list[DiscoveryTarget]:
    targets = []
    for role in decision_maker_roles:
        query = quote_plus(f'"{employer}" "{role}"')
        targets.append(DiscoveryTarget(
            employer=employer,
            role=role,
            query=query,
            rationale=f"Public-source research for {role} at {employer}",
        ))
    return targets
