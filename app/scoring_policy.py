import json
from pathlib import Path

DEFAULT_POLICY = {
    "weights": {"signal_high": 10, "leadership_new": 12, "signal_medium": 6, "signal_low": 2, "momentum_max_bonus": 15, "momentum_max_penalty": 8},
    "thresholds": {"pursue": 70, "monitor": 40},
    "caps": {"minimum": 0, "maximum": 100},
}

def load_policy(path='config/scoring.json'):
    p=Path(path)
    if not p.exists(): return DEFAULT_POLICY
    data=json.loads(p.read_text(encoding='utf-8'))
    return {**DEFAULT_POLICY, **data, 'weights':{**DEFAULT_POLICY['weights'], **data.get('weights',{})}, 'thresholds':{**DEFAULT_POLICY['thresholds'], **data.get('thresholds',{})}, 'caps':{**DEFAULT_POLICY['caps'], **data.get('caps',{})}}

def score_signal(signal, policy):
    w=policy['weights']
    if signal.severity=='high' and signal.kind=='leadership_new': return w['leadership_new']
    return w.get(f"signal_{signal.severity}",0)

def classify_score(score, policy):
    t=policy['thresholds']
    if score>=t['pursue']: return 'Pursue'
    if score>=t['monitor']: return 'Monitor'
    return 'Low'
