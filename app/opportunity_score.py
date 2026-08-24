from .signals import HiringSignal
from .employer_momentum import employer_momentum_bonus


def calculate_opportunity_score(base_score: int, signals: list[HiringSignal], momentum: dict) -> int:
    score = max(0, min(100, base_score))
    for signal in signals:
        if signal.severity == 'high':
            score += 12 if signal.kind == 'leadership_new' else 10
        elif signal.severity == 'medium':
            score += 6
        else:
            score += 2
    score += employer_momentum_bonus(momentum)
    return max(0, min(100, score))


def priority_for_score(score: int) -> str:
    if score >= 70: return 'Pursue'
    if score >= 40: return 'Monitor'
    return 'Low'
