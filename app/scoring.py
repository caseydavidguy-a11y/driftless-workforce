from dataclasses import dataclass
from .models import Employer

@dataclass(frozen=True)
class ScoreBreakdown:
    opening_volume: int
    hiring_momentum: int
    target_industry: int
    leadership_signal: int
    source_quality: int

    @property
    def total(self) -> int:
        return min(100, self.opening_volume + self.hiring_momentum + self.target_industry + self.leadership_signal + self.source_quality)


def score_employer(employer: Employer) -> ScoreBreakdown:
    count = employer.opening_count
    verified = employer.verified_opening_count
    opening_volume = min(30, count * 5)
    hiring_momentum = min(25, max(0, (count - 1) * 4))
    target_industry = 20 if employer.industries else 0
    leadership_signal = min(15, sum("manager" in o.title.lower() or "supervisor" in o.title.lower() or "director" in o.title.lower() for o in employer.observations) * 5)
    source_quality = 10 if verified else 3
    return ScoreBreakdown(opening_volume, hiring_momentum, target_industry, leadership_signal, source_quality)


def apply_score(employer: Employer) -> Employer:
    breakdown = score_employer(employer)
    employer.score = breakdown.total
    employer.priority = "Pursue" if employer.score >= 70 else "Monitor" if employer.score >= 40 else "Low"
    return employer
