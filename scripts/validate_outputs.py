"""Validate generated Driftless intelligence artifacts before publication."""
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/"data"
REQUIRED_OPPORTUNITY={"employer","slug","score","priority","opening_count","verified_opening_count","locations","industries","score_breakdown","score_policy_version"}; REQUIRED_JOB={"employer","title","location","industry","source","source_url","external_id","verified"}; REQUIRED_SIGNAL={"employer","kind","severity","message","metric"}
def load(name):
    path=DATA/name
    if not path.exists():raise ValueError(f"missing artifact: {name}")
    return json.loads(path.read_text(encoding="utf-8"))
def validate():
    opportunities=load("employer_opportunities.json")
    if not isinstance(opportunities,list):raise ValueError("employer_opportunities.json must be a list")
    seen=set()
    for row in opportunities:
        missing=REQUIRED_OPPORTUNITY-set(row)
        if missing:raise ValueError(f"opportunity missing fields: {sorted(missing)}")
        if row["slug"] in seen:raise ValueError(f"duplicate employer slug: {row['slug']}")
        seen.add(row["slug"])
        if not 0<=row["score"]<=100:raise ValueError(f"invalid score for {row['employer']}")
        if row["priority"] not in {"Pursue","Monitor","Low"}:raise ValueError(f"invalid priority for {row['employer']}")
        if row["opening_count"]<0 or row["verified_opening_count"]<0:raise ValueError(f"invalid opening count for {row['employer']}")
        if row["verified_opening_count"]>row["opening_count"]:raise ValueError(f"verified openings exceed openings for {row['employer']}")
        if not isinstance(row["score_breakdown"],list):raise ValueError(f"score breakdown missing for {row['employer']}")
    import csv
    jobs_path=DATA/"current_jobs.csv"
    if jobs_path.exists():
        with jobs_path.open(newline="",encoding="utf-8") as h:
            for row in csv.DictReader(h):
                missing=REQUIRED_JOB-set(row)
                if missing:raise ValueError(f"job missing fields: {sorted(missing)}")
    signals=load("signals.json")
    if not isinstance(signals,list):raise ValueError("signals.json must be a list")
    for signal in signals:
        missing=REQUIRED_SIGNAL-set(signal)
        if missing:raise ValueError(f"signal missing fields: {sorted(missing)}")
        if signal["severity"] not in {"high","medium","low"}:raise ValueError(f"invalid signal severity: {signal['severity']}")
    history=load("snapshot_history.json"); snapshots=history.get("snapshots",history) if isinstance(history,(dict,list)) else []
    if not isinstance(snapshots,list):raise ValueError("snapshot history must contain a list")
    if len(snapshots)>60:raise ValueError("snapshot history exceeds 60 captures")
    print(f"Validated {len(opportunities)} opportunities, {len(signals)} signals, and {len(snapshots)} snapshots.")
if __name__=="__main__":validate()
