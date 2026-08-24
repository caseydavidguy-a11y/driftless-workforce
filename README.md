# Driftless Workforce — Employer Intelligence Engine

Driftless Workforce is building a La Crosse-area employer intelligence and recruiting prospecting engine. The first release turns local hiring activity into normalized employer opportunities that can be scored and prioritized for recruiting outreach.

## V1 scope

- Geographic focus: La Crosse area
- Target industries: manufacturing, warehouse, operations, skilled trades, hospitality, leadership
- Live source connector: Wisconsin Job Center public job-search results
- Employer normalization and deduplication
- Hiring-history tracking
- Evidence/source tracking
- 0–100 employer opportunity scoring
- Pursue / Monitor / Low prioritization
- Change detection foundation
- Dashboard/API-ready output
- Demo data is explicitly separated from verified source data

## Repository layout

- `app/` — domain models, normalization, scoring, pipeline, and source connectors
- `data/` — generated job and employer-opportunity outputs
- `tests/` — automated tests and source-parser fixtures
- `docs/` — architecture and operating notes
- `scripts/` — runnable collection and demo entry points
- `.github/workflows/` — scheduled data refresh automation

## Quick start

Requires Python 3.11+.

```bash
python -m unittest discover -s tests -v
python scripts/run_demo.py
python scripts/collect_jobcenter.py
```

The live collector searches La Crosse, Onalaska, Holmen, and West Salem and preserves source URLs, posting dates, employer names, and verification status. The GitHub Actions workflow refreshes the live intelligence dataset daily and commits changes when the data changes.

The demo intentionally uses clearly marked sample records. Production connectors must preserve source URLs and timestamps for every verified observation.
