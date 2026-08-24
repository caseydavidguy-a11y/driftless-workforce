from __future__ import annotations
import re

def _tokens(value): return {x for x in re.findall(r"[a-z0-9+#.-]+", (value or '').lower()) if len(x)>1}

def match_candidate(candidate, search):
    skills=_tokens(candidate.get('skills','')); required=_tokens(search.get('requirements',''))
    overlap=skills & required
    skill_score=round(len(overlap)/len(required)*70) if required else 0
    location_score=20 if not search.get('location') or candidate.get('location','').lower()==search.get('location','').lower() else 0
    availability_score=10 if candidate.get('available',True) else 0
    score=min(100,skill_score+location_score+availability_score)
    return {'candidate_id':candidate.get('id'),'search_id':search.get('id'),'score':score,'matched_skills':sorted(overlap),'recommendation':'Strong match' if score>=75 else 'Review' if score>=50 else 'Weak match'}

def rank_candidates(candidates, search):
    return sorted((match_candidate(c,search) for c in candidates), key=lambda x:x['score'], reverse=True)
