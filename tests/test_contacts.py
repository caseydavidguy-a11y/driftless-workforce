import unittest

from app.contacts import build_contact_targets
from app.prospecting import ProspectProfile


class ContactResearchTests(unittest.TestCase):
    def test_targets_rank_roles_without_personal_data(self):
        prospect = ProspectProfile(
            employer="Example Manufacturing",
            score=82,
            priority="Pursue",
            hiring_summary="Example Manufacturing has 3 observed openings across 1 local location(s).",
            reasons=("Leadership hiring signal",),
            target_roles=("leadership", "manufacturing / production"),
            industries=("manufacturing",),
            decision_maker_roles=("HR / Talent Acquisition", "Hiring Manager"),
            contact_path="Use official/public sources.",
            outreach_angle="Lead with capacity.",
            evidence=("Production Supervisor — La Crosse [job center]",),
        )

        targets = build_contact_targets(prospect)

        self.assertGreaterEqual(len(targets), 2)
        self.assertEqual(targets[0].priority, 100)
        self.assertIn("HR / Talent Acquisition", targets[0].role)
        self.assertTrue(all("@" not in query for target in targets for query in target.search_queries))
        self.assertTrue(all("email" not in path.lower() for target in targets for path in target.public_contact_paths))


if __name__ == "__main__":
    unittest.main()
