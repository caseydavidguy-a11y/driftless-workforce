# Driftless Workforce — Employer Intelligence + Recruiting Workspace

Driftless Workforce is a La Crosse-area employer intelligence and recruiting prospecting engine. It turns local hiring activity into normalized employer opportunities that can be scored, explained, tracked over time, and prioritized for recruiting outreach. The static command center also includes a browser-persistent recruiting workspace for employer records, contacts, candidates, active searches, and candidate-to-search matching.

## Intelligence capabilities

- Geographic focus: La Crosse area
- Target industries: manufacturing, warehouse, operations, skilled trades, hospitality, leadership
- Live source connector: Wisconsin Job Center public job-search results
- Employer normalization and cross-city deduplication
- Hiring-history snapshots and 7-day/30-day employer-specific momentum
- Evidence/source tracking
- Configurable 0–100 employer opportunity scoring
- Explainable score breakdowns with scoring-policy versioning
- Pursue / Monitor / Low prioritization
- Change detection and persisted change reports
- Prospect profiles with recommended outreach paths
- Production output validation before generated data is committed

## Recruiting workspace

Open `frontend/workspace.html` from the deployed Pages site to manage:

- Employers
- Contacts
- Candidates and skills
- Active recruiting searches
- Candidate-to-search matching with ranked scores

Workspace records are intentionally stored in browser `localStorage` for this static deployment. **Do not put sensitive candidate/client information into the Pages workspace yet.** A production deployment with authenticated access, encrypted server-side storage, backups, audit logs, and explicit privacy/retention controls is required before handling protected or confidential recruiting records.

## Repository layout

- `app/` — domain models, normalization, scoring, matching, history, pipeline, and source connectors
- `config/` — versioned scoring policy
- `data/` — generated production outputs; populated by the refresh workflow
- `tests/` — automated tests and source-parser fixtures
- `docs/` — architecture and operating notes
- `scripts/` — runnable collection, demo, and output-validation entry points
- `frontend/` — GitHub Pages command center, prospect profiles, pipeline, and recruiting workspace
- `.github/workflows/` — tests, scheduled/live refresh, and Pages deployment

## Quick start

Requires Python 3.11+.

```bash
python -m unittest discover -s tests -v
python scripts/run_demo.py
python scripts/collect_jobcenter.py
python scripts/validate_outputs.py
```

The live collector searches La Crosse, Onalaska, Holmen, and West Salem. It preserves source URLs, posting dates, employer names, and verification status, deduplicates repeated observations, and persists a current snapshot, a rolling 60-capture history, and a change report.

GitHub Actions runs the collector after code changes and daily on schedule. The refresh workflow runs the complete test suite and production-output validation before committing generated data. The Pages workflow publishes only the frontend and generated intelligence artifacts; application source and scoring configuration are not published as part of the site artifact.

The scoring model is configurable in `config/scoring.json`. Every generated opportunity includes the active scoring-policy version and a point-by-point explanation. `data/demo_employer_opportunities.json` and `scripts/run_demo.py` are for demonstration only; production intelligence starts empty and is populated by the live refresh workflow.

## Production boundary

The intelligence engine is production-oriented. The browser CRM is a functional static prototype, not a secure multi-user CRM. The final production step for handling real candidate/client records is deployment of the same domain model behind an authenticated API/database with secrets, access control, encryption, backups, audit logging, and privacy/retention policies. Those controls cannot safely be simulated with GitHub Pages/localStorage.