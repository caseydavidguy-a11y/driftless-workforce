# Driftless Workforce — Employer Intelligence Engine

Driftless Workforce is building a La Crosse-area employer intelligence and recruiting prospecting engine. The first release turns local hiring activity into normalized employer opportunities that can be scored and prioritized for recruiting outreach.

## V1 scope

- Geographic focus: La Crosse area
- Target industries: manufacturing, warehouse, operations, skilled trades, hospitality, leadership
- Initial source architecture: Wisconsin Job Center / Wisconsin workforce job data
- Employer normalization and deduplication
- Hiring-history tracking
- Evidence/source tracking
- 0–100 employer opportunity scoring
- Pursue / Monitor / Low prioritization
- Change detection for new or increased hiring activity
- Dashboard/API-ready output
- Demo data is explicitly separated from verified source data

## Repository layout

- `app/` — core domain models, scoring, normalization, and pipeline logic
- `data/` — local sample/demo inputs and generated output locations
- `tests/` — automated tests
- `docs/` — architecture and operating notes
- `scripts/` — runnable collection/scoring entry points

## Quick start

Requires Python 3.11+.

```bash
python -m unittest discover -s tests -v
python scripts/run_demo.py
```

The demo intentionally uses clearly marked sample records. Production connectors must preserve source URLs and timestamps for every verified observation.
