from datetime import datetime, timezone

def hiring_momentum(snapshots, days=7):
    if not snapshots: return {"days":days,"change":0,"pct":0,"direction":"flat"}
    ordered=sorted(snapshots,key=lambda x:x.get('captured_at',''))
    latest=ordered[-1]
    cutoff=(datetime.fromisoformat(latest['captured_at'].replace('Z','+00:00'))).timestamp()-days*86400
    eligible=[s for s in ordered if datetime.fromisoformat(s['captured_at'].replace('Z','+00:00')).timestamp()>=cutoff]
    if len(eligible)<2: return {"days":days,"change":0,"pct":0,"direction":"baseline"}
    old=sum(e.get('opening_count',0) for e in eligible[0].get('employers',[]))
    new=sum(e.get('opening_count',0) for e in eligible[-1].get('employers',[]))
    change=new-old; pct=round(change/old*100) if old else (100 if new else 0)
    return {"days":days,"change":change,"pct":pct,"direction":"up" if change>0 else "down" if change<0 else "flat"}

def momentum_bonus(momentum):
    if momentum['direction']=='up': return min(15, max(3, momentum['pct']//10 + (5 if momentum['change']>=3 else 0)))
    if momentum['direction']=='down': return -min(8, abs(momentum['pct'])//10)
    return 0

def momentum_label(momentum):
    if momentum['direction']=='up': return 'Rising'
    if momentum['direction']=='down': return 'Cooling'
    if momentum['direction']=='baseline': return 'Baseline'
    return 'Stable'
