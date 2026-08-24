"""Build public-contact research targets from qualified employer prospects.

This module deliberately does not guess personal contact data. It creates
structured, auditable research targets that a later verified-discovery step
can populate.
"""
from dataclasses import dataclass, asdict
from urllib.parse import quote_plus

from .prospecting import ProspectProfile

@dataclass(frozen=True)
class ContactResearchTarget:
    employer: str
    priority: str
    decision_maker_role: str
    search_queries: tuple[str, ...]
    official_site_query: str
    professional_profile_query: str
    status: str = "needs_research"


def build_contact_target(prospect: ProspectProfile) -> ContactResearchTarget:
    role = prospect.decision_maker_roles[0] if prospect.decision_maker_roles else "HR / Talent Acquisition"
    q1 = f'"{prospect.employer}" "{role}" La Crosse Wisconsin'
    q2 = f'"{prospect.employer}" human resources talent acquisition La Crosse'
    return ContactResearchTarget(
        employer=prospect.employer,
        priority=prospect.priority,
        decision_maker_role=role,
        search_queries=(q1, q2),
        official_site_query=f'"{prospect.employer}" official website careers contact',
        professional_profile_query=f'"{prospect.employer}" "{role}" LinkedIn',
    )


def search_links(target: ContactResearchTarget) -> dict:
    return {
        "web_search": [f"https://www.google.com/search?q={quote_plus(q)}" for q in target.search_queries],
        "official_site_search": f"https://www.google.com/search?q={quote_plus(target.official_site_query)}",
        "professional_profile_search": f"https://www.google.com/search?q={quote_plus(target.professional_profile_query)}",
    }


def serialize_target(target: ContactResearchTarget) -> dict:
    data = asdict(target)
    data["search_links"] = search_links(target)
    return data
