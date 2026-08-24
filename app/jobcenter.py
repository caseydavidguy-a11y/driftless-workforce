"""Job Center of Wisconsin job-search connector.

The public Job Center search is HTML, so this connector intentionally keeps
source-specific parsing here and converts records into the engine's generic
JobObservation model.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from html.parser import HTMLParser
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .models import JobObservation

BASE_URL = "https://www.jobcenterofwisconsin.com/Presentation/JobSeekers/JobOrderList.aspx"


class _TableParser(HTMLParser):
    """Small dependency-free parser for the Job Center results table."""

    def __init__(self) -> None:
        super().__init__()
        self.in_row = False
        self.in_cell = False
        self.cell_text: list[str] = []
        self.row: list[str] = []
        self.rows: list[list[str]] = []

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag == "tr":
            self.in_row = True
            self.row = []
        elif self.in_row and tag in {"td", "th"}:
            self.in_cell = True
            self.cell_text = []

    def handle_data(self, data):
        if self.in_cell:
            self.cell_text.append(data)

    def handle_endtag(self, tag):
        tag = tag.lower()
        if self.in_row and tag in {"td", "th"} and self.in_cell:
            text = " ".join("".join(self.cell_text).split())
            self.row.append(text)
            self.in_cell = False
        elif tag == "tr" and self.in_row:
            if self.row:
                self.rows.append(self.row)
            self.in_row = False


def _fetch(url: str, timeout: int = 30) -> str:
    request = Request(
        url,
        headers={
            "User-Agent": "DriftlessWorkforce/1.0 (+https://github.com/caseydavidguy-a11y/driftless-workforce)"
        },
    )
    with urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8", errors="replace")


def build_search_url(city: str) -> str:
    params = {
        "Appr": "False",
        "MOSCode": "",
        "STCode": "",
        "city": city,
        "dist": "",
        "edu": "",
        "kwords": "",
        "loc": city,
        "loctyp": "City",
        "onet": "",
        "shft": "",
        "src": "JCW,PARTNERS",
        "tbsel": "N",
        "wd": "",
        "ww": "",
    }
    return f"{BASE_URL}?{urlencode(params)}"


def _parse_date(text: str) -> datetime | None:
    try:
        return datetime.strptime(text.strip(), "%m/%d/%Y").replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def infer_industry(title: str) -> str:
    value = title.lower()
    if any(word in value for word in ("manufactur", "production", "assembler", "fabricat", "machine operator", "process technician")):
        return "manufacturing"
    if any(word in value for word in ("warehouse", "distribution", "logistics", "fulfillment", "material handler")):
        return "warehouse"
    if any(word in value for word in ("supervisor", "manager", "director", "team lead", "leader", "foreman")):
        return "leadership"
    if any(word in value for word in ("maintenance", "electrician", "welder", "mechanic", "technician", "hvac", "plumber")):
        return "skilled trades"
    if any(word in value for word in ("restaurant", "cook", "server", "barista", "food service", "hotel", "hospitality")):
        return "hospitality"
    if "operations" in value or "operational" in value:
        return "operations"
    return ""


def _split_employer(first_cell: str) -> tuple[str, str]:
    """Extract title/employer from JCW's combined first result cell.

    Current rendered results place the employer after the title and before
    metadata such as "Pay:" or "Source:". Employers are displayed in
    uppercase, which gives us a stable parsing boundary without guessing from
    the job title itself.
    """
    clean = " ".join(first_cell.split())
    cutoff = re.split(r"\s+(?:Pay:|Source:|On Busline|On-Site|Remote)\b", clean, maxsplit=1, flags=re.I)[0]
    match = re.search(r"(?P<employer>[A-Z][A-Z0-9&.,'()\-/ ]{2,})$", cutoff)
    if not match:
        return clean, ""
    employer = re.sub(r"\s+", " ", match.group("employer")).strip(" ,.-")
    title = clean[: match.start("employer")].strip(" -–—")
    return title, employer


def parse_results(html: str, source_url: str, requested_city: str) -> list[JobObservation]:
    parser = _TableParser()
    parser.feed(html)
    observations: list[JobObservation] = []

    for row in parser.rows:
        if len(row) < 3 or row[0].lower() == "title":
            continue
        first_cell, location, date_posted = row[:3]
        if not first_cell or not location or not date_posted:
            continue

        title, employer = _split_employer(first_cell)
        if not employer or not title or not _parse_date(date_posted):
            continue

        external_id = f"jcw:{requested_city.lower()}:{title.lower()}:{date_posted}:{employer.lower()}"
        observations.append(
            JobObservation(
                employer=employer,
                title=title,
                location=location,
                industry=infer_industry(title),
                posted_at=_parse_date(date_posted),
                source="Job Center of Wisconsin",
                source_url=source_url,
                external_id=external_id,
                verified=True,
            )
        )

    return observations


def fetch_city(city: str) -> list[JobObservation]:
    url = build_search_url(city)
    return parse_results(_fetch(url), url, city)


def fetch_area(cities: tuple[str, ...] = ("La Crosse", "Onalaska", "Holmen", "West Salem")) -> list[JobObservation]:
    observations: list[JobObservation] = []
    for city in cities:
        observations.extend(fetch_city(city))
    return observations
