import unittest

from app.jobcenter import build_search_url, build_job_search_url, infer_industry, parse_results


FIXTURE = """
<table>
<tr><th>Title</th><th>Location</th><th>Date Posted</th></tr>
<tr><td>Production Supervisor TRANE TECHNOLOGIES Source: USNLX</td><td>La Crosse</td><td>07/31/2026</td></tr>
<tr><td>2nd Shift Line/Utility Job Details GREAT LAKES CHEESE Source: USNLX</td><td>La Crosse</td><td>08/18/2026</td></tr>
<tr><td>Police Officer CITY OF LA CROSSE Pay: $69,160.00 Per Year to $83,116.00 Per Year On Busline Source: Job Center of Wisconsin</td><td>La Crosse</td><td>07/30/2026</td></tr>
</table>
"""


class JobCenterTests(unittest.TestCase):
    def test_search_url_contains_city_filter(self):
        url = build_search_url("La Crosse")
        self.assertIn("city=La+Crosse", url)
        self.assertIn("loctyp=City", url)

    def test_job_search_url_contains_title_and_employer(self):
        url = build_job_search_url("Production Supervisor", "TRANE TECHNOLOGIES", "La Crosse")
        self.assertIn("kwords=Production+Supervisor+TRANE+TECHNOLOGIES", url)
        self.assertIn("city=La+Crosse", url)

    def test_industry_inference(self):
        self.assertEqual(infer_industry("Production Supervisor"), "manufacturing")
        self.assertEqual(infer_industry("Maintenance Supervisor"), "leadership")
        self.assertEqual(infer_industry("Warehouse Associate"), "warehouse")

    def test_parse_combined_first_cell(self):
        observations = parse_results(FIXTURE, "https://example.test/jobs", "La Crosse")
        self.assertEqual(len(observations), 3)
        self.assertEqual(observations[0].title, "Production Supervisor")
        self.assertEqual(observations[0].employer, "TRANE TECHNOLOGIES")
        self.assertEqual(observations[0].industry, "manufacturing")
        self.assertTrue(observations[0].verified)
        self.assertEqual(observations[2].employer, "CITY OF LA CROSSE")
        self.assertIn("kwords=Production+Supervisor+TRANE+TECHNOLOGIES", observations[0].source_url)


if __name__ == "__main__":
    unittest.main()
