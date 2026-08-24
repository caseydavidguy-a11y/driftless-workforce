from datetime import datetime

def employer_momentum(snapshots, slug, days=7):
    ordered=sorted(snapshots,key=lambda x:x.get('captured_at',''))
    if not ordered:return {'days':days,'change':0,'pct':0,'direction':'baseline','points':[]}
    latest_dt=datetime.fromisoformat(ordered[-1]['captured_at'].replace('Z','+00:00'))
    cutoff=latest_dt.timestamp()-days*86400
    points=[]
    for s in ordered:
        dt=datetime.fromisoformat(s['captured_at'].replace('Z','+00:00'))
        if dt.timestamp()<cutoff:continue
        e=next((x for x in s.get('employers',[]) if x.get('slug')==slug),None)
        if e:points.append({'captured_at':s['captured_at'],'opening_count':e.get('opening_count',0)})
    if len(points)<2:return {'days':days,'change':0,'pct':0,'direction':'baseline','points':points}
    old,new=points[0]['opening_count'],points[-1]['opening_count']; change=new-old
    pct=round(change/old*100) if old else (100 if new else 0)
    return {'days':days,'change':change,'pct':pct,'direction':'up' if change>0 else 'down' if change<0 else 'flat','points':points}

def employer_momentum_bonus(m):
    if m['direction']=='up':return min(15,max(3,m['pct']//10+(5 if m['change']>=3 else 0)))
    if m['direction']=='down':return -min(8,abs(m['pct'])//10)
    return 0
