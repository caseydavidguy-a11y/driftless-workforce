from .signals import HiringSignal
from .employer_momentum import employer_momentum_bonus


def explain_score(base_score: int, signals: list[HiringSignal], momentum: dict) -> dict:
    base = max(0, min(100, base_score))
    items = [{"label": "Base opportunity", "points": base, "reason": "Underlying employer/opportunity fit"}]
    for s in signals:
        points = 12 if s.severity == 'high' and s.kind == 'leadership_new' else 10 if s.severity == 'high' else 6 if s.severity == 'medium' else 2
        items.append({"label": s.kind.replace('_',' ').title(), "points": points, "reason": s.message})
    mp = employer_momentum_bonus(momentum)
    if mp: items.append({"label": "Hiring momentum", "points": mp, "reason": f"{momentum.get('direction','stable').title()} {momentum.get('pct',0):+}% over {momentum.get('days',7)} days"})
    total=max(0,min(100,sum(x['points'] for x in items)))
    return {"score":total,"items":items,"capped":sum(x['points'] for x in items)>100}
