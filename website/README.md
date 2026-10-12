# Driftless Workforce Group public website

Static site for Driftless Workforce Group, built from one Python script with no outside packages.

    python3 website/build.py     # writes website/out (the site) and website/preview

- Pages and forms are defined in `build.py`. The forms and the Google Sheet backend share one field list.
- `apps-script/` is the forms backend and private inbox (Google Apps Script). Setup steps: `apps-script/SETUP.md`.
- `qr.py` makes print-ready QR codes and checks each one by scanning it.
- GitHub Pages builds and publishes `website/out` on every push to `main` (`.github/workflows/pages.yml`).

To connect the forms, put the Apps Script "Forms" web app address in `SITE['endpoint']` in `build.py`,
and the "Inbox" address in `SITE['inbox_url']`.
