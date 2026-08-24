from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

INDUSTRIES = (
    "manufacturing",
    "warehouse",
    "operations",
    "skilled trades",
    "hospitality",
    "leadership",
)

@dataclass(frozen=True)
class JobObservation:
    employer: str
    title: str
    location: str
    industry: str
    posted_at: Optional[datetime] = None
    source: str = "unknown"
    source_url: str = ""
    external_id: str = ""
    verified: bool = False

@dataclass
class Employer:
    name: str
    canonical_name: str
    locations: set[str] = field(default_factory=set)
    industries: set[str] = field(default_factory=set)
    observations: list[JobObservation] = field(default_factory=list)
    score: int = 0
    priority: str = "Low"

    @property
    def opening_count(self) -> int:
        return len(self.observations)

    @property
    def verified_opening_count(self) -> int:
        return sum(o.verified for o in self.observations)
