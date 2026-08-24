import unittest
from app.outreach import OutreachRecord

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
