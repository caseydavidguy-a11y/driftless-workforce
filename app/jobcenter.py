"""Job Center of Wisconsin job-search connector."""
from __future__ import annotations
import re
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone
from html.parser import HTMLParser
from urllib.parse import urlencode,urljoin
from urllib.request import Request,urlopen
from .models import JobObservation
BASE_URL="https://jobcenterofwisconsin.com/Presentation/JobSeekers/JobOrderList.aspx"
class _TableParser(HTMLParser):
    def __init__(self):
        super().__init__(); self.in_row=False; self.in_cell=False; self.cell_text=[]; self.cell_href=""; self.row=[]; self.rows=[]; self.row_links=[]
    def handle_starttag(self,tag,attrs):
        tag=tag.lower(); attrs=dict(attrs)
        if tag=="tr":
            self.in_row=True; self.row=[]; self.row_first_href=""
        elif self.in_row and tag in {"td","th"}:
            self.in_cell=True; self.cell_text=[]; self.cell_href=""
        if self.in_row and not getattr(self,"row_first_href",""):
            for key in ("href","data-href","data-url"):
                value=attrs.get(key,"")
                if value and ("JobOrder" in value or "job" in value.lower()):
                    self.row_first_href=value; break
            if not self.row_first_href:
                onclick=attrs.get("onclick","")
                match=re.search(r"""['"]((?:https?:)?//[^'"]+|[^'"]*JobOrder[^'"]*)['"]""",onclick,re.I)
                if match:self.row_first_href=match.group(1)
        if self.in_cell and tag=="a" and not self.cell_href:
            self.cell_href=attrs.get("href","")
    def handle_data(self,data):
        if self.in_cell:self.cell_text.append(data)
    def handle_endtag(self,tag):
        tag=tag.lower()
        if self.in_row and tag in {"td","th"} and self.in_cell:
            self.row.append(" ".join("".join(self.cell_text).split()));
            if not getattr(self,"row_first_href",""):self.row_first_href=self.cell_href
            self.in_cell=False
        elif tag=="tr" and self.in_row:
            if self.row:self.rows.append(self.row); self.row_links.append(self.row_first_href)
            self.in_row=False
def _fetch(url,timeout=30):
    headers={"User-Agent":"Mozilla/5.0 (compatible; DriftlessWorkforce/1.1; +https://github.com/caseydavidguy-a11y/driftless-workforce)","Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8","Accept-Language":"en-US,en;q=0.9","Referer":"https://jobcenterofwisconsin.com/"}
    candidates=(url, url.replace("https://jobcenterofwisconsin.com/","https://www.jobcenterofwisconsin.com/"))
    last=None
    for candidate in candidates:
        for attempt in range(3):
            try:
                request=Request(candidate,headers=headers)
                with urlopen(request,timeout=timeout) as response:
                    body=response.read().decode("utf-8",errors="replace")
                    if len(body)>500:
                        return body
                    last=RuntimeError(f"JCW returned an unexpectedly small response ({len(body)} bytes)")
            except Exception as exc:
                last=exc
    raise RuntimeError(f"JCW request failed after retries: {last}")
def build_search_url(city):
    params={"Appr":"False","MOSCode":"","STCode":"","city":city,"dist":"","edu":"","kwords":"","loc":city,"loctyp":"City","onet":"","shft":"","src":"JCW,PARTNERS","tbsel":"N","wd":"","ww":""}; return f"{BASE_URL}?{urlencode(params)}"

def build_job_search_url(title, employer, city):
    """Build a job-specific JCW search when the result row has no direct href."""
    keywords=f"{title} {employer}".strip()
    params={"Appr":"False","MOSCode":"","STCode":"","city":city,"dist":"","edu":"","kwords":keywords,"loc":city,"loctyp":"City","onet":"","shft":"","src":"JCW,PARTNERS","tbsel":"N","wd":"","ww":""}
    return f"{BASE_URL}?{urlencode(params)}"
def _parse_date(text):
    try:return datetime.strptime(text.strip(),"%m/%d/%Y").replace(tzinfo=timezone.utc)
    except ValueError:return None
def infer_industry(title):
    value=title.lower()
    if any(k in value for k in ("restaurant","cook","food","barista","crew member","server")):return "hospitality"
    if any(k in value for k in ("production","operator","manufacturing","fabrication","quality")):return "manufacturing"
    if any(k in value for k in ("manager","supervisor","director","lead","chief")):return "leadership"
    if any(k in value for k in ("warehouse","shipping","receiving","material","inventory","stock","freight")):return "warehouse"
    if any(k in value for k in ("maintenance","technician","mechanic","lineworker","electrician","hvac","trades")):return "skilled trades"
    return "operations"
def _split_combined_first_cell(text):
    before_source=text.split("Source:",1)[0].strip(); before_source=re.sub(r"\s+(?:Pay:|On Busline|Image:).*?$","",before_source,flags=re.I).strip(); match=re.search(r"\s([A-Z][A-Z0-9 &.,'’/-]{2,})$",before_source)
    if match:return before_source[:match.start()].strip(),match.group(1).strip()
    return before_source,""
def parse_results(html,source_url,requested_city):
    parser=_TableParser(); parser.feed(html); observations=[]
    for index,row in enumerate(parser.rows):
        if len(row)<3:continue
        if len(row)>=4:title,location,date_posted,employer=row[:4]; employer=employer.split("Source:",1)[0].strip()
        else:title,employer=_split_combined_first_cell(row[0]); location,date_posted=row[1:3]
        if not title or not location or not date_posted or not employer or title.lower()=="title":continue
        row_href=parser.row_links[index] if index<len(parser.row_links) else ""
        detail_url=urljoin(source_url,row_href) if row_href else build_job_search_url(title,employer,requested_city)
        if detail_url.rstrip("/") == source_url.rstrip("/"):
            detail_url=build_job_search_url(title,employer,requested_city)
        external_id=f"jcw:{requested_city.lower()}:{title.lower()}:{date_posted}:{employer.lower()}"
        observations.append(JobObservation(employer=employer,title=title,location=location,industry=infer_industry(title),posted_at=_parse_date(date_posted),source="Job Center of Wisconsin",source_url=detail_url,external_id=external_id,verified=True))
    return observations
def fetch_city(city):
    url=build_search_url(city); return parse_results(_fetch(url),url,city)
def _rss_candidates():
    return [
        "https://jobcenterofwisconsin.com/rss.aspx",
        "https://www.jobcenterofwisconsin.com/services/rss.aspx",
    ]
def parse_rss(xml_text):
    root=ET.fromstring(xml_text); observations=[]
    for item in root.findall(".//item"):
        title=(item.findtext("title") or "").strip(); link=(item.findtext("link") or "").strip(); desc=(item.findtext("description") or "").strip()
        if not title or not link: continue
        posted=None
        pub=item.findtext("pubDate")
        if pub:
            try: posted=parsedate_to_datetime(pub).astimezone(timezone.utc)
            except (TypeError,ValueError): pass
        observations.append((title,link,desc,posted))
    return observations

def fetch_rss():
    for url in _rss_candidates():
        try:
            xml=_fetch(url); return parse_rss(xml)
        except Exception: continue
    return []

def fetch_area(cities=("La Crosse","Onalaska","Holmen","West Salem")):
    observations=[]; seen=set(); failures=[]
    for city in cities:
        try:
            city_observations=fetch_city(city)
        except Exception as exc:
            failures.append(f"{city}: {exc}")
            continue
        for observation in city_observations:
            if observation.external_id in seen:continue
            seen.add(observation.external_id); observations.append(observation)
    if not observations and failures:
        raise RuntimeError("All JCW area searches failed — " + " | ".join(failures))
    return observations
