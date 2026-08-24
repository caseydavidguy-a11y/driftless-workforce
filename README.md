# Driftless Workforce — Employer Intelligence Engine

Driftless Workforce is building a La Crosse-area employer intelligence and recruiting prospecting engine. The first release turns local hiring activity into normalized employer opportunities that can be scored, explained, tracked over time, and prioritized for recruiting outreach.

## V1 scope

- Geographic focus: La Crosse area
- Target industries: manufacturing, warehouse, operations, skilled trades, hospitality, leadership
- Live source connector: Wisconsin Job Center public job-search results
- Employer normalization and deduplication
- Hiring-history snapshots and 7-day employer-specific momentum
- Evidence/source tracking
- Configurable 0–100 employer opportunity scoring
- Explainable score breakdowns with scoring-policy versioning
- Pursue / Monitor / Low prioritization
- Change detection and persisted change reports
- Prospect profiles with recommended outreach paths
- Dashboard/API-ready output
- Demo data is explicitly separated from verified source data

## Repository layout

- `app/` — domain models, normalization, scoring, history, pipeline, and source connectors
- `config/` — versioned scoring policy
- `data/` — generated job, snapshot, change, contact, and employer-opportunity outputs
- `tests/` — automated tests and source-parser fixtures
- `docs/` — architecture and operating notes
- `scripts/` — runnable collection and demo entry points
- `.github/workflows/` — tests, scheduled data refresh, and Pages deployment

## Quick start

Requires Python 3.11+.

```bash
python -m unittest discover -s tests -v
python scripts/run_demo.py
python scripts/collect_jobcenter.py
```

The live collector searches La Crosse, Onalaska, Holmen, and West Salem and preserves source URLs, posting dates, employer names, and verification status. Each refresh persists a current snapshot, a rolling 60-capture history, and a change report. GitHub Actions refreshes the live intelligence dataset daily and commits changed outputs.

The scoring model is deliberately configurable in `config/scoring.json`. Every generated opportunity includes the active scoring-policy version and a point-by-point explanation. The demo intentionally uses clearly marked sample records. Production connectors must preserve source URLs and timestamps for every verified observation.
