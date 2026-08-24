from .opportunity_score import calculate_opportunity_score, priority_for_score
from .score_explanation import explain_score
from .scoring_policy import load_policy


def audit_score(base_score, signals, momentum, policy=None):
    policy = policy or load_policy()
    score = calculate_opportunity_score(base_score, signals, momentum, policy)
    explanation = explain_score(base_score, signals, momentum, policy)
    return {
        "policy_version": policy.get("version", 1),
        "score": score,
        "priority": priority_for_score(score, policy),
        "explanation": explanation,
    }
