import unittest

from app.models import Employer, JobObservation
from app.prospecting import build_prospect, build_prospect_list


class ProspectingTests(unittest.TestCase):
    def test_build_prospect_explains_leadership_signal(self):
        employer = Employer(name="Example Manufacturing", canonical_name="example manufacturing")
        employer.observations.extend([
            JobObservation("Example Manufacturing", "Production Supervisor", "La Crosse", "manufacturing", verified=True),
            JobObservation("Example Manufacturing", "Maintenance Technician", "La Crosse", "skilled trades", verified=True),
        ])
        employer.locations.add("La Crosse")
        employer.industries.update({"manufacturing", "skilled trades"})
        employer.score = 75
        employer.priority = "Pursue"

        prospect = build_prospect(employer)

        self.assertEqual(prospect.priority, "Pursue")
        self.assertIn("leadership", prospect.target_roles)
        self.assertTrue(any("Leadership hiring signal" in reason for reason in prospect.reasons))
        self.assertIn("recruiting", prospect.outreach_angle.lower())
        self.assertIn("HR / Talent Acquisition", prospect.decision_maker_roles)
        self.assertIn("Hiring Manager", prospect.decision_maker_roles)
        self.assertNotIn("@", prospect.contact_path)

    def test_evidence_is_traceable_to_source_observation(self):
        employer = Employer(name="Local Employer", canonical_name="local employer")
        employer.observations.append(
            JobObservation("Local Employer", "Warehouse Lead", "Onalaska", "warehouse", source="JCW", verified=True)
        )
        employer.locations.add("Onalaska")
        employer.industries.add("warehouse")

        prospect = build_prospect(employer)

        self.assertEqual(len(prospect.evidence), 1)
        self.assertIn("Warehouse Lead", prospect.evidence[0])
        self.assertIn("JCW", prospect.evidence[0])

    def test_single_opening_still_creates_actionable_reason(self):
        employer = Employer(name="Local Employer", canonical_name="local employer")
        employer.observations.append(
            JobObservation("Local Employer", "Warehouse Associate", "Onalaska", "warehouse", verified=True)
        )
        employer.locations.add("Onalaska")
        employer.industries.add("warehouse")

        prospect = build_prospect(employer)

        self.assertEqual(prospect.hiring_summary, "Local Employer has 1 observed opening(s) across 1 local location(s).")
        self.assertTrue(prospect.reasons)
        self.assertIn("warehouse", prospect.target_roles[0])

    def test_prospect_list_is_score_ordered(self):
        low = Employer(name="Low", canonical_name="low")
        low.observations.append(JobObservation("Low", "Operator", "La Crosse", "manufacturing"))
        high = Employer(name="High", canonical_name="high")
        high.observations.extend([
            JobObservation("High", "Supervisor", "La Crosse", "manufacturing", verified=True)
            for _ in range(8)
        ])
        high.score = 90
        high.priority = "Pursue"
        low.score = 20
        low.priority = "Low"

        prospects = build_prospect_list([low, high])
        self.assertEqual(prospects[0].employer, "High")
        self.assertEqual(prospects[1].employer, "Low")


if __name__ == "__main__":
    unittest.main()
