"""Collect current La Crosse-area JCW openings and produce prospect-ready data."""

from __future__ import annotations

import csv
import json
from dataclasses import asdict
from pathlib import Path

from app.jobcenter import fetch_area
from app.pipeline import build_employers

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)


def main() -> None:
    observations = fetch_area()
    employers = build_employers(observations)

    with (DATA / "current_jobs.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=[
            "employer", "title", "location", "industry", "posted_at",
            "source", "source_url", "external_id", "verified",
        ])
        writer.writeheader()
        for observation in observations:
            row = asdict(observation)
            row["posted_at"] = row["posted_at"].isoformat() if row["posted_at"] else ""
            writer.writerow(row)

    with (DATA / "employer_opportunities.json").open("w", encoding="utf-8") as handle:
        json.dump([
            {
                "employer": employer.name,
                "score": employer.score,
                "priority": employer.priority,
                "opening_count": employer.opening_count,
                "verified_opening_count": employer.verified_opening_count,
                "locations": sorted(employer.locations),
                "industries": sorted(employer.industries),
                "jobs": [
                    {
                        "title": job.title,
                        "location": job.location,
                        "posted_at": job.posted_at.isoformat() if job.posted_at else None,
                        "source_url": job.source_url,
                    }
                    for job in employer.observations
                ],
            }
            for employer in employers
        ], handle, indent=2)

    print(f"Collected {len(observations)} openings from {len(employers)} employers.")


if __name__ == "__main__":
    main()
