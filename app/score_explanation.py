from .signals import HiringSignal
from .employer_momentum import employer_momentum_bonus
from .scoring_policy import load_policy, score_signal


def explain_score(base_score: int, signals: list[HiringSignal], momentum: dict, policy: dict | None = None) -> dict:
    policy = policy or load_policy()
    caps = policy['caps']
    base = max(caps['minimum'], min(caps['maximum'], base_score))
    items = [{"label": "Base opportunity", "points": base, "reason": "Underlying employer/opportunity fit"}]
    for signal in signals:
        points = score_signal(signal, policy)
        items.append({"label": signal.kind.replace('_', ' ').title(), "points": points, "reason": signal.message})
    raw_momentum = employer_momentum_bonus(momentum)
    mp = max(-policy['weights']['momentum_max_penalty'], min(policy['weights']['momentum_max_bonus'], raw_momentum))
    if mp:
        items.append({"label": "Hiring momentum", "points": mp, "reason": f"{momentum.get('direction', 'stable').title()} {momentum.get('pct', 0):+}% over {momentum.get('days', 7)} days"})
    raw_total = sum(x['points'] for x in items)
    total = max(caps['minimum'], min(caps['maximum'], raw_total))
    return {"score": total, "items": items, "capped": raw_total != total, "policy_version": policy.get("version", 1)}
