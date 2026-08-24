import unittest
from app.contact_research import build_contact_target, search_links
from app.prospecting import ProspectProfile

class ContactResearchTests(unittest.TestCase):
    def test_target_is_auditable_and_does_not_invent_contact(self):
        prospect = ProspectProfile(
            employer="Example Manufacturing",
            score=82,
            priority="Pursue",
            hiring_summary="3 openings",
            reasons=("Active hiring",),
            target_roles=("manufacturing / production",),
            industries=("manufacturing",),
            decision_maker_roles=("HR / Talent Acquisition", "Hiring Manager"),
            contact_path="Research official/public sources",
            outreach_angle="Discuss recruiting support",
            evidence=("Operator — La Crosse, WI",),
        )
        target = build_contact_target(prospect)
        self.assertEqual(target.status, "needs_research")
        self.assertIn("Example Manufacturing", target.search_queries[0])
        self.assertIn("official", target.official_site_query)
        links = search_links(target)
        self.assertTrue(links["web_search"])
        self.assertNotIn("email", target.__dict__)
        self.assertNotIn("phone", target.__dict__)

if __name__ == "__main__":
    unittest.main()
