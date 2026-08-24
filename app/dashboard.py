from .models import Employer

STATUS_ORDER = ("NEW", "RESEARCHING", "CONTACT IDENTIFIED", "CONTACTED", "ENGAGED", "CLIENT")


def dashboard_rows(employers: list[Employer]) -> list[dict]:
    rows = []
    for employer in sorted(employers, key=lambda e: (-e.score, e.name.lower())):
        leadership = [
            o.title for o in employer.observations
            if any(word in o.title.lower() for word in ("manager", "supervisor", "director", "lead"))
        ]
        rows.append({
            "employer": employer.name,
            "score": employer.score,
            "priority": employer.priority,
            "openings": employer.opening_count,
            "verified_openings": employer.verified_opening_count,
            "industries": sorted(employer.industries),
            "locations": sorted(employer.locations),
            "leadership_openings": leadership,
            "status": "NEW",
            "next_action": "Research decision-maker" if employer.priority == "Pursue" else "Monitor hiring activity",
        })
    return rows


def pipeline_summary(rows: list[dict]) -> dict:
    return {
        "total": len(rows),
        "pursue": sum(r["priority"] == "Pursue" for r in rows),
        "monitor": sum(r["priority"] == "Monitor" for r in rows),
        "low": sum(r["priority"] == "Low" for r in rows),
    }
