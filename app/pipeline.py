from collections import defaultdict
from .models import Employer, JobObservation
from .normalize import canonicalize_employer, normalize_industry
from .scoring import apply_score
from .change_report import employer_from_snapshot


def build_employers(observations: list[JobObservation], previous_snapshot: dict | None = None, snapshots: list[dict] | None = None) -> list[Employer]:
    grouped: dict[str, list[JobObservation]] = defaultdict(list)
    for observation in observations:
        grouped[canonicalize_employer(observation.employer)].append(observation)

    previous = {
        item.get("slug", item.get("name", "")): employer_from_snapshot(item)
        for item in (previous_snapshot or {}).get("employers", [])
    }
    employers: list[Employer] = []
    has_previous_feed = previous_snapshot is not None
    for key, jobs in grouped.items():
        employer = Employer(name=jobs[0].employer, canonical_name=key)
        employer.observations.extend(jobs)
        employer.locations.update(j.location for j in jobs if j.location)
        employer.industries.update(normalize_industry(j.industry) for j in jobs if j.industry)
        prior = previous.get(key)
        if prior is None and has_previous_feed:
            prior = Employer(name=employer.name, canonical_name=key)
        apply_score(employer, prior, snapshots)
        employers.append(employer)
    return sorted(employers, key=lambda e: (-e.score, e.canonical_name))
