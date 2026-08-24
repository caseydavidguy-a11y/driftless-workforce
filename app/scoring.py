from dataclasses import dataclass
from .models import Employer
from .signals import HiringSignal, compare_employer
from .employer_momentum import employer_momentum_bonus
from .opportunity_score import calculate_opportunity_score, priority_for_score
from .score_explanation import explain_score


@dataclass(frozen=True)
class ScoreBreakdown:
    opening_volume: int
    target_industry: int
    source_quality: int
    signal_points: int
    hiring_momentum: int

    @property
    def total(self) -> int:
        return min(100, self.opening_volume + self.target_industry + self.source_quality + self.signal_points + self.hiring_momentum)


def _base_score(employer: Employer) -> tuple[int, int, int]:
    opening_volume = min(30, employer.opening_count * 5)
    target_industry = 15 if employer.industries else 0
    source_quality = 10 if employer.verified_opening_count else 3
    return opening_volume + target_industry + source_quality, opening_volume, target_industry + source_quality


def score_employer(employer: Employer, previous: Employer | None = None, snapshots: list[dict] | None = None) -> ScoreBreakdown:
    base, opening_volume, fit = _base_score(employer)
    signals = compare_employer(employer, previous)
    momentum = {"direction": "baseline", "pct": 0, "change": 0, "days": 7}
    if snapshots is not None:
        from .employer_momentum import employer_momentum
        momentum = employer_momentum(snapshots, employer.canonical_name, 7)
    score = calculate_opportunity_score(base, signals, momentum)
    signal_points = max(0, score - base - employer_momentum_bonus(momentum))
    momentum_points = employer_momentum_bonus(momentum)
    return ScoreBreakdown(opening_volume, fit, 0, signal_points, momentum_points)


def apply_score(employer: Employer, previous: Employer | None = None, snapshots: list[dict] | None = None) -> Employer:
    base, _, _ = _base_score(employer)
    signals = compare_employer(employer, previous)
    momentum = {"direction": "baseline", "pct": 0, "change": 0, "days": 7}
    if snapshots is not None:
        from .employer_momentum import employer_momentum
        momentum = employer_momentum(snapshots, employer.canonical_name, 7)
    employer.score = calculate_opportunity_score(base, signals, momentum)
    employer.priority = priority_for_score(employer.score)
    return employer


def score_explanation(employer: Employer, previous: Employer | None = None, snapshots: list[dict] | None = None) -> dict:
    base, _, _ = _base_score(employer)
    signals = compare_employer(employer, previous)
    momentum = {"direction": "baseline", "pct": 0, "change": 0, "days": 7}
    if snapshots is not None:
        from .employer_momentum import employer_momentum
        momentum = employer_momentum(snapshots, employer.canonical_name, 7)
    return explain_score(base, signals, momentum)
