import unittest

from app.models import JobObservation
from app.normalize import canonicalize_employer
from app.pipeline import build_employers

class EngineTests(unittest.TestCase):
    def test_canonicalize_employer(self):
        self.assertEqual(canonicalize_employer("Acme, Inc."), "acme")
        self.assertEqual(canonicalize_employer("ACME LLC"), "acme")

    def test_groups_same_employer(self):
        jobs=[JobObservation("Acme, Inc.","Operator","La Crosse, WI","manufacturing"),JobObservation("ACME LLC","Supervisor","La Crosse, WI","leadership")]
        employers=build_employers(jobs)
        self.assertEqual(len(employers),1); self.assertEqual(employers[0].opening_count,2)

    def test_first_snapshot_is_baseline(self):
        jobs=[JobObservation("Acme","Operator","La Crosse, WI","manufacturing",verified=True)]*8
        employer=build_employers(jobs)[0]
        self.assertEqual(employer.score,55)
        self.assertEqual(employer.priority,"Monitor")

    def test_new_employer_after_baseline_gets_hiring_signal(self):
        jobs=[JobObservation("Acme","Operator","La Crosse, WI","manufacturing",verified=True)]
        employer=build_employers(jobs, {"captured_at":"2026-08-23T00:00:00+00:00","employers":[]})[0]
        self.assertEqual(employer.score,30+10)

    def test_priority_is_assigned(self):
        jobs=[JobObservation("Acme","Operator","La Crosse, WI","manufacturing",verified=True)]*8
        employer=build_employers(jobs)[0]
        self.assertIn(employer.priority,{"Pursue","Monitor","Low"}); self.assertGreaterEqual(employer.score,0); self.assertLessEqual(employer.score,100)

if __name__=="__main__":unittest.main()
