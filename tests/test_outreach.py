import unittest
from app.outreach import OutreachRecord, build_outreach_draft

class OutreachTests(unittest.TestCase):
    def test_new_to_researching(self):
        record = OutreachRecord("Acme")
        record.advance("RESEARCHING")
        self.assertEqual(record.status, "RESEARCHING")

    def test_contact_requires_name(self):
        record = OutreachRecord("Acme")
        with self.assertRaises(ValueError):
            record.advance("CONTACT IDENTIFIED")

    def test_contact_can_be_verified_with_source(self):
        record = OutreachRecord("Acme")
        record.advance("RESEARCHING")
        record.advance("CONTACT IDENTIFIED", contact_name="Jane Doe", contact_source_url="https://example.com/team")
        self.assertEqual(record.contact_name, "Jane Doe")
        self.assertEqual(record.status, "CONTACT IDENTIFIED")

if __name__ == "__main__":
    unittest.main()


    def test_draft_requires_verified_contact(self):
        with self.assertRaises(ValueError):
            build_outreach_draft({"employer":"Acme"}, {})

    def test_draft_requires_approval_and_never_auto_sends(self):
        draft=build_outreach_draft({"employer":"Acme","opening_count":2,"target_roles":["Maintenance"],"outreach_angle":"Recent hiring activity suggests a need for support."}, {"name":"Jane Doe","title":"Talent Acquisition Manager","source_url":"https://example.com/hr"})
        self.assertEqual(draft["state"],"draft")
        self.assertTrue(draft["approval_required"])
        self.assertFalse(draft["auto_send"])
        self.assertIn("Maintenance",draft["body"])
