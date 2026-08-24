from datetime import datetime
from .models import Employer, JobObservation
from .signals import compare_employer


def _parse_dt(value):
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def employer_from_snapshot(item: dict) -> Employer:
    observations = []
    for raw in item.get("observations", []):
        row = dict(raw)
        row["posted_at"] = _parse_dt(row.get("posted_at"))
        observations.append(JobObservation(**row))
    employer = Employer(name=item["name"], canonical_name=item.get("slug", item["name"]))
    employer.locations.update(item.get("locations", []))
    employer.industries.update(item.get("industries", []))
    employer.observations.extend(observations)
    return employer


def compare_snapshots(previous: dict, current: dict) -> dict:
    old = {x["slug"]: employer_from_snapshot(x) for x in previous.get("employers", [])}
    new = {x["slug"]: employer_from_snapshot(x) for x in current.get("employers", [])}
    report = []
    for slug, employer in new.items():
        signals = compare_employer(employer, old.get(slug))
        if signals:
            report.append({"employer": employer.name, "slug": slug, "signals": [s.__dict__ for s in signals]})
    removed = sorted(old.keys() - new.keys())
    return {"previous": previous.get("captured_at"), "current": current.get("captured_at"), "changes": report, "removed_employers": removed}
