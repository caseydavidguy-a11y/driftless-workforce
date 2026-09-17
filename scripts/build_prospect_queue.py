"""Build a contact-ready prospect queue from the generated employer intelligence."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "data" / "employer_opportunities.json"
DEFAULT_OUTPUT = ROOT / "data" / "prospect_queue.json"


def build_queue(records: list[dict], minimum_score: int = 0, limit: int | None = None) -> list[dict]:
    queue = []
    for item in records:
        score = int(item.get("score", 0))
        if score < minimum_score:
            continue
        queue.append({
            "employer": item.get("employer", ""),
            "slug": item.get("slug", ""),
            "score": score,
            "priority": item.get("priority", "Low"),
            "opening_count": item.get("opening_count", 0),
            "verified_opening_count": item.get("verified_opening_count", 0),
            "locations": item.get("locations", []),
            "industries": item.get("industries", []),
            "target_roles": item.get("target_roles", []),
            "decision_maker_roles": item.get("decision_maker_roles", []),
            "contact_path": item.get("contact_path", ""),
            "outreach_angle": item.get("outreach_angle", ""),
            "evidence": item.get("evidence", []),
            "jobs": item.get("jobs", []),
            "status": "new",
            "contact": None,
            "outreach": {"state": "not_started", "next_action": None},
        })
    queue.sort(key=lambda x: (-x["score"], -x["verified_opening_count"], -x["opening_count"], x["slug"]))
    return queue[:limit] if limit else queue


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--minimum-score", type=int, default=0)
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()

    records = json.loads(args.input.read_text(encoding="utf-8"))
    queue = build_queue(records, args.minimum_score, args.limit or None)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(queue, indent=2), encoding="utf-8")
    print(f"Wrote {len(queue)} prospects to {args.output}")


if __name__ == "__main__":
    main()
