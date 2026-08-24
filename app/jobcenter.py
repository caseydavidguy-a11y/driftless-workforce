"""Job Center of Wisconsin job-search connector."""
from __future__ import annotations
import re
from datetime import datetime, timezone
from html.parser import HTMLParser
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from .models import JobObservation

BASE_URL="https://www.jobcenterofwisconsin.com/Presentation/JobSeekers/JobOrderList.aspx"
class _TableParser(HTMLParser):
    def __init__(self):
        super().__init__(); self.in_row=False; self.in_cell=False; self.cell_text=[]; self.row=[]; self.rows=[]
    def handle_starttag(self,tag,attrs):
        tag=tag.lower()
        if tag=="tr": self.in_row=True; self.row=[]
        elif self.in_row and tag in {"td","th"}: self.in_cell=True; self.cell_text=[]
    def handle_data(self,data):
        if self.in_cell:self.cell_text.append(data)
    def handle_endtag(self,tag):
        tag=tag.lower()
        if self.in_row and tag in {"td","th"} and self.in_cell:
            self.row.append(" ".join("".join(self.cell_text).split())); self.in_cell=False
        elif tag=="tr" and self.in_row:
            if self.row:self.rows.append(self.row)
            self.in_row=False

def _fetch(url,timeout=30):
    request=Request(url,headers={"User-Agent":"DriftlessWorkforce/1.0 (+https://github.com/caseydavidguy-a11y/driftless-workforce)"})
    with urlopen(request,timeout=timeout) as response:return response.read().decode("utf-8",errors="replace")
def build_search_url(city):
    params={"Appr":"False","MOSCode":"","STCode":"","city":city,"dist":"","edu":"","kwords":"","loc":city,"loctyp":"City","onet":"","shft":"","src":"JCW,PARTNERS","tbsel":"N","wd":"","ww":""}
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
    before_source=text.split("Source:",1)[0].strip()
    before_source=re.sub(r"\s+(?:Pay:|On Busline|Image:).*?$","",before_source,flags=re.I).strip()
    match=re.search(r"\s([A-Z][A-Z0-9 &.,'’/-]{2,})$",before_source)
    if match:return before_source[:match.start()].strip(),match.group(1).strip()
    return before_source,""
def parse_results(html,source_url,requested_city):
    parser=_TableParser(); parser.feed(html); observations=[]
    for row in parser.rows:
        if len(row)<3:continue
        if len(row)>=4:
            title,location,date_posted,employer=row[:4]; employer=employer.split("Source:",1)[0].strip()
        else:title,employer=_split_combined_first_cell(row[0]); location,date_posted=row[1:3]
        if not title or not location or not date_posted or not employer or title.lower()=="title":continue
        external_id=f"jcw:{requested_city.lower()}:{title.lower()}:{date_posted}:{employer.lower()}"
        observations.append(JobObservation(employer=employer,title=title,location=location,industry=infer_industry(title),posted_at=_parse_date(date_posted),source="Job Center of Wisconsin",source_url=source_url,external_id=external_id,verified=True))
    return observations
def fetch_city(city):
    url=build_search_url(city); return parse_results(_fetch(url),url,city)
def fetch_area(cities=("La Crosse","Onalaska","Holmen","West Salem")):
    observations=[]; seen=set()
    for city in cities:
        for observation in fetch_city(city):
            if observation.external_id in seen:continue
            seen.add(observation.external_id); observations.append(observation)
    return observations
