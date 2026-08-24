import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from .models import Employer


def snapshot_record(employers: list[Employer], captured_at: str | None = None) -> dict:
    return {
        "captured_at": captured_at or datetime.now(timezone.utc).isoformat(),
        "employers": [
            {
                "name": e.name,
                "slug": e.slug,
                "opening_count": e.opening_count,
                "verified_opening_count": e.verified_opening_count,
                "industries": sorted(e.industries),
                "locations": sorted(e.locations),
                "observations": [asdict(o) for o in e.observations],
            }
            for e in employers
        ],
    }


def write_snapshot(path: str | Path, employers: list[Employer], captured_at: str | None = None) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(snapshot_record(employers, captured_at), indent=2), encoding="utf-8")


def read_snapshot(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))
