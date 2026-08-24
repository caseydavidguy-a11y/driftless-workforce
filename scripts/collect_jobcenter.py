"""Collect current La Crosse-area JCW openings and produce prospect-ready data."""
from __future__ import annotations
import csv,json
from dataclasses import asdict
from pathlib import Path
from app.change_report import compare_snapshots, employer_from_snapshot
from app.contacts import build_contact_targets
from app.employer_momentum import employer_momentum
from app.jobcenter import fetch_area
from app.pipeline import build_employers
from app.prospecting import build_prospect_list
from app.snapshots import read_snapshot,snapshot_record,write_snapshot
from app.scoring import score_explanation
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/"data"; DATA.mkdir(exist_ok=True)
SNAPSHOT_PATH=DATA/"snapshot_current.json"; HISTORY_PATH=DATA/"snapshot_history.json"
def _load_history():
    if not HISTORY_PATH.exists():return []
    try:
        data=json.loads(HISTORY_PATH.read_text(encoding="utf-8")); return data.get("snapshots",[]) if isinstance(data,dict) else data
    except (OSError,json.JSONDecodeError):return []
def _save_history(history): HISTORY_PATH.write_text(json.dumps({"snapshots":history[-60:]},indent=2),encoding="utf-8")
def main():
    try:
        observations=fetch_area()
    except Exception as exc:
        print(f"Job Center fetch failed: {exc}")
        observations=[]
    history=_load_history()
    previous=read_snapshot(SNAPSHOT_PATH) if SNAPSHOT_PATH.exists() else None
    if previous is not None and not previous.get("employers"): previous=None
    if not observations:
        print("No live observations collected; preserving the last successful intelligence snapshot.")
        return
    employers=build_employers(observations,previous,history); prospects=build_prospect_list(employers)
    previous_employers={item.get("slug",item.get("name","")):employer_from_snapshot(item) for item in (previous or {}).get("employers",[])}
    with (DATA/"current_jobs.csv").open("w",newline="",encoding="utf-8") as handle:
        writer=csv.DictWriter(handle,fieldnames=["employer","title","location","industry","posted_at","source","source_url","external_id","verified"]); writer.writeheader()
        for observation in observations:
            row=asdict(observation); row["posted_at"]=row["posted_at"].isoformat() if row["posted_at"] else ""; writer.writerow(row)
    prospect_by_name={p.employer:p for p in prospects}; opportunity_rows=[]
    for employer in employers:
        prospect=prospect_by_name[employer.name]; explanation=score_explanation(employer,previous_employers.get(employer.canonical_name),history); momentum_7d=employer_momentum(history,employer.canonical_name,7); momentum_30d=employer_momentum(history,employer.canonical_name,30)
        opportunity_rows.append({"employer":employer.name,"slug":employer.canonical_name,"score":employer.score,"priority":employer.priority,"opening_count":employer.opening_count,"verified_opening_count":employer.verified_opening_count,"locations":sorted(employer.locations),"industries":sorted(employer.industries),"hiring_summary":prospect.hiring_summary,"reasons":list(prospect.reasons),"target_roles":list(prospect.target_roles),"industries_detected":list(prospect.industries),"decision_maker_roles":list(prospect.decision_maker_roles),"contact_path":prospect.contact_path,"outreach_angle":prospect.outreach_angle,"evidence":list(prospect.evidence),"momentum_7d":momentum_7d,"momentum_30d":momentum_30d,"score_breakdown":explanation["items"],"score_policy_version":explanation["policy_version"],"score_policy_capped":explanation["capped"],"jobs":[{"title":job.title,"location":job.location,"posted_at":job.posted_at.isoformat() if job.posted_at else None,"source_url":job.source_url} for job in employer.observations]})
    (DATA/"employer_opportunities.json").write_text(json.dumps(opportunity_rows,indent=2),encoding="utf-8")
    contact_research=[{"employer":prospect.employer,"score":prospect.score,"priority":prospect.priority,"targets":[asdict(target) for target in build_contact_targets(prospect)]} for prospect in prospects]
    (DATA/"contact_research.json").write_text(json.dumps(contact_research,indent=2),encoding="utf-8")
    current=snapshot_record(employers); report=compare_snapshots(previous,current) if previous else {"previous":None,"current":current["captured_at"],"changes":[],"removed_employers":[]}
    (DATA/"change_report.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    signals=[{"employer":change["employer"],**signal} for change in report["changes"] for signal in change["signals"]]
    (DATA/"signals.json").write_text(json.dumps(signals,indent=2),encoding="utf-8")
    history.append(current); _save_history(history); write_snapshot(SNAPSHOT_PATH,employers,current["captured_at"])
    print(f"Collected {len(observations)} openings from {len(employers)} employers.")
    for prospect in prospects[:10]:
        targets=build_contact_targets(prospect); print(f"- {prospect.employer}: {prospect.score}/100 ({prospect.priority}) — {prospect.hiring_summary}"); print(f"  Contact targets: {', '.join(t.role for t in targets[:3])}"); print(f"  Angle: {prospect.outreach_angle}")
if __name__=="__main__":main()
