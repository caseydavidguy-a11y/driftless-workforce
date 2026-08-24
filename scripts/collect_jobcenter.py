"""Collect current La Crosse-area JCW openings and produce prospect-ready data."""

from __future__ import annotations

import csv
import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from app.change_report import compare_snapshots
from app.contacts import build_contact_targets
from app.jobcenter import fetch_area
from app.pipeline import build_employers
from app.prospecting import build_prospect_list
from app.snapshots import read_snapshot, snapshot_record, write_snapshot
from app.scoring import score_explanation

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)
SNAPSHOT_PATH = DATA / "snapshot_current.json"
HISTORY_PATH = DATA / "snapshot_history.json"


def _load_history() -> list[dict]:
    if not HISTORY_PATH.exists():
        return []
    try:
        data = json.loads(HISTORY_PATH.read_text(encoding="utf-8"))
        return data.get("snapshots", []) if isinstance(data, dict) else data
    except (OSError, json.JSONDecodeError):
        return []


def _save_history(history: list[dict]) -> None:
    # Keep the last 60 captures so momentum can evolve without making the repo grow forever.
    HISTORY_PATH.write_text(json.dumps({"snapshots": history[-60:]}, indent=2), encoding="utf-8")


def main() -> None:
    observations = fetch_area()
    previous = read_snapshot(SNAPSHOT_PATH) if SNAPSHOT_PATH.exists() else None
    history = _load_history()
    employers = build_employers(observations, previous, history)
    prospects = build_prospect_list(employers)

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

    prospect_by_name = {p.employer: p for p in prospects}
    opportunity_rows = []
    for employer in employers:
        prospect = prospect_by_name[employer.name]
        explanation = score_explanation(employer, None if not previous else next((
            __import__("app.change_report", fromlist=["employer_from_snapshot"]).employer_from_snapshot(x)
            for x in previous.get("employers", []) if x.get("slug") == employer.canonical_name
        ), history)
        opportunity_rows.append({
            "employer": employer.name,
            "slug": employer.canonical_name,
            "score": employer.score,
            "priority": employer.priority,
            "opening_count": employer.opening_count,
            "verified_opening_count": employer.verified_opening_count,
            "locations": sorted(employer.locations),
            "industries": sorted(employer.industries),
            "hiring_summary": prospect.hiring_summary,
            "reasons": list(prospect.reasons),
            "target_roles": list(prospect.target_roles),
            "industries_detected": list(prospect.industries),
            "decision_maker_roles": list(prospect.decision_maker_roles),
            "contact_path": prospect.contact_path,
            "outreach_angle": prospect.outreach_angle,
            "evidence": list(prospect.evidence),
            "score_breakdown": explanation["items"],
            "score_policy_capped": explanation["capped"],
            "jobs": [
                {
                    "title": job.title,
                    "location": job.location,
                    "posted_at": job.posted_at.isoformat() if job.posted_at else None,
                    "source_url": job.source_url,
                }
                for job in employer.observations
            ],
        })

    with (DATA / "employer_opportunities.json").open("w", encoding="utf-8") as handle:
        json.dump(opportunity_rows, handle, indent=2)

    contact_research = []
    for prospect in prospects:
        contact_research.append({
            "employer": prospect.employer,
            "score": prospect.score,
            "priority": prospect.priority,
            "targets": [asdict(target) for target in build_contact_targets(prospect)],
        })
    with (DATA / "contact_research.json").open("w", encoding="utf-8") as handle:
        json.dump(contact_research, handle, indent=2)

    current = snapshot_record(employers)
    if previous:
        report = compare_snapshots(previous, current)
        (DATA / "change_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    history.append(current)
    _save_history(history)
    write_snapshot(SNAPSHOT_PATH, employers, current["captured_at"])

    print(f"Collected {len(observations)} openings from {len(employers)} employers.")
    print("Top prospects:")
    for prospect in prospects[:10]:
        targets = build_contact_targets(prospect)
        print(f"- {prospect.employer}: {prospect.score}/100 ({prospect.priority}) — {prospect.hiring_summary}")
        print(f"  Contact targets: {', '.join(t.role for t in targets[:3])}")
        print(f"  Angle: {prospect.outreach_angle}")


if __name__ == "__main__":
    main()
