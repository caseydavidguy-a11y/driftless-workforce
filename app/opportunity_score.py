from .signals import HiringSignal
from .employer_momentum import employer_momentum_bonus
from .scoring_policy import load_policy, score_signal, classify_score


def calculate_opportunity_score(base_score: int, signals: list[HiringSignal], momentum: dict, policy: dict | None = None) -> int:
    policy = policy or load_policy()
    caps = policy['caps']
    score = max(caps['minimum'], min(caps['maximum'], base_score))
    for signal in signals:
        score += score_signal(signal, policy)
    momentum_points = employer_momentum_bonus(momentum)
    score += max(-policy['weights']['momentum_max_penalty'], min(policy['weights']['momentum_max_bonus'], momentum_points))
    return max(caps['minimum'], min(caps['maximum'], score))


def priority_for_score(score: int, policy: dict | None = None) -> str:
    return classify_score(score, policy or load_policy())
