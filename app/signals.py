from dataclasses import dataclass
from datetime import datetime, timezone
from .models import Employer

@dataclass(frozen=True)
class HiringSignal:
    kind: str
    severity: str
    message: str
    metric: str


def compare_employer(current: Employer, previous: Employer | None) -> list[HiringSignal]:
    if previous is None:
        return []
    signals=[]
    old=previous.opening_count; new=current.opening_count
    if old == 0 and new > 0:
        signals.append(HiringSignal("hiring_started", "high", f"Hiring activity started with {new} opening(s)", f"{new} openings"))
    elif new > old:
        pct=round(((new-old)/old)*100) if old else 100
        severity="high" if pct>=50 or new-old>=3 else "medium"
        signals.append(HiringSignal("volume_increase",severity,f"Openings increased from {old} to {new} ({pct}% increase)",f"+{new-old} / {pct}%"))
    elif new < old:
        signals.append(HiringSignal("volume_decrease","low",f"Openings decreased from {old} to {new}",f"{new-old}"))
    old_titles={o.title.strip().lower() for o in previous.observations}
    for o in current.observations:
        title=o.title.strip().lower()
        if title not in old_titles and any(w in title for w in ("manager","supervisor","director","lead")):
            signals.append(HiringSignal("leadership_new","high",f"New leadership opening: {o.title}",o.title))
    return signals


def signal_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()
