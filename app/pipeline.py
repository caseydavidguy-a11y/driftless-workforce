from collections import defaultdict
from .models import Employer, JobObservation
from .normalize import canonicalize_employer, normalize_industry
from .scoring import apply_score


def build_employers(observations: list[JobObservation]) -> list[Employer]:
    grouped: dict[str, list[JobObservation]] = defaultdict(list)
    for observation in observations:
        grouped[canonicalize_employer(observation.employer)].append(observation)

    employers: list[Employer] = []
    for key, jobs in grouped.items():
        employer = Employer(name=jobs[0].employer, canonical_name=key)
        employer.observations.extend(jobs)
        employer.locations.update(j.location for j in jobs if j.location)
        employer.industries.update(normalize_industry(j.industry) for j in jobs if j.industry)
        apply_score(employer)
        employers.append(employer)
    return sorted(employers, key=lambda e: (-e.score, e.canonical_name))
