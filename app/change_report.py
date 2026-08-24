from .models import Employer, JobObservation
from .signals import compare_employer


def employer_from_snapshot(item: dict) -> Employer:
    observations=[JobObservation(**o) for o in item.get("observations", [])]
    return Employer(
        item["name"], item["slug"], observations=observations,
        verified_opening_count=item.get("verified_opening_count", 0)
    )


def compare_snapshots(previous: dict, current: dict) -> dict:
    old={x["slug"]: employer_from_snapshot(x) for x in previous.get("employers", [])}
    new={x["slug"]: employer_from_snapshot(x) for x in current.get("employers", [])}
    report=[]
    for slug, employer in new.items():
        signals=compare_employer(employer, old.get(slug))
        if signals:
            report.append({"employer": employer.name, "signals": [s.__dict__ for s in signals]})
    removed=sorted(old.keys()-new.keys())
    return {"previous": previous.get("captured_at"), "current": current.get("captured_at"), "changes": report, "removed_employers": removed}
