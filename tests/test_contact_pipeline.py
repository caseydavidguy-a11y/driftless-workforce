import unittest
from app.contact_pipeline import ProspectRecord, ProspectStatus, PublicContact
from app.contact_discovery import build_discovery_targets

class ContactPipelineTests(unittest.TestCase):
    def test_unverified_contact_is_rejected(self):
        record = ProspectRecord("Example Co")
        with self.assertRaises(ValueError):
            record.add_contact(PublicContact("Example Co", "HR / Talent Acquisition"))
        self.assertEqual(record.status, ProspectStatus.NEW)

    def test_verified_contact_advances_pipeline(self):
        record = ProspectRecord("Example Co")
        record.add_contact(PublicContact("Example Co", "HR / Talent Acquisition", "Jane Example", "https://example.com/team", "official_site"))
        self.assertEqual(record.status, ProspectStatus.CONTACT_IDENTIFIED)
        record.mark_contacted("email")
        self.assertEqual(record.status, ProspectStatus.CONTACTED)
        record.mark_engaged("Asked about hard-to-fill production roles")
        self.assertEqual(record.status, ProspectStatus.ENGAGED)

    def test_discovery_targets_are_role_specific(self):
        targets = build_discovery_targets("Trane Technologies", ("HR / Talent Acquisition", "Hiring Manager"))
        self.assertEqual(len(targets), 2)
        self.assertIn("Trane+Technologies", targets[0].query)

if __name__ == "__main__":
    unittest.main()
