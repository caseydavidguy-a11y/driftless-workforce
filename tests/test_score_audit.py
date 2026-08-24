import unittest
from app.score_audit import audit_score
from app.signals import HiringSignal

class ScoreAuditTests(unittest.TestCase):
    def test_audit_contains_policy_and_priority(self):
        result = audit_score(55, [HiringSignal('leadership_new','high','New supervisor opening','Supervisor')], {'direction':'up','pct':100,'change':5,'days':7})
        self.assertEqual(result['policy_version'], 1)
        self.assertEqual(result['score'], 77)
        self.assertEqual(result['priority'], 'Pursue')
        self.assertTrue(result['explanation']['items'])

if __name__ == '__main__': unittest.main()
