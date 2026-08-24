# Production deployment boundary

## Intelligence site

The employer intelligence command center is deployable to GitHub Pages. It publishes generated intelligence only.

## Recruiting API

The secure recruiting API lives in `server/` and is designed for a managed container host plus PostgreSQL. Required environment variables:

- `DATABASE_URL`
- `DRIFTLESS_JWT_SECRET`
- `PORT` (optional; defaults to 8000)

Start locally:

```bash
cd server
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
export DRIFTLESS_JWT_SECRET="a-long-random-secret"
export DATABASE_URL="sqlite:///./driftless.db"
uvicorn main:app --reload
```

Production should use PostgreSQL, HTTPS, a secret manager, database backups, restricted CORS, rate limiting, and separate staging/production databases. Never commit `.env`, database credentials, JWT secrets, or candidate documents.

The current Pages workspace deliberately remains a localStorage fallback. It must not be used for confidential candidate/client records until the authenticated API is connected and deployed.

## Definition of done for confidential CRM data

- authenticated users
- password hashing
- short-lived signed access tokens
- PostgreSQL persistence
- HTTPS-only API
- role/permission model
- audit logging
- backups and recovery test
- retention/deletion policy
- CORS allowlist
- rate limiting
- frontend API integration
- production smoke test
