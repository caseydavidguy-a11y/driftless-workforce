from .models import Employer
from .signals import HiringSignal


def signal_bonus(signals: list[HiringSignal]) -> int:
    """Return a bounded V1 bonus so fresh hiring signals can affect priority."""
    bonus = 0
    for signal in signals:
        if signal.severity == "high":
            bonus += 12 if signal.kind == "leadership_new" else 10
        elif signal.severity == "medium":
            bonus += 6
        else:
            bonus += 2
    return min(25, bonus)


def score_with_signals(base_score: int, signals: list[HiringSignal]) -> int:
    return min(100, max(0, base_score + signal_bonus(signals)))


def priority_for_score(score: int) -> str:
    if score >= 70:
        return "Pursue"
    if score >= 40:
        return "Monitor"
    return "Low"
