import unittest

from app.models import Employer, JobObservation
from app.scout import build_prospect_queue, prospect_to_dict


class ScoutTests(unittest.TestCase):
    def test_queue_filters_and_sorts(self):
        low = Employer(name="Low Co", canonical_name="low-co", score=20, priority="Low")
        high = Employer(name="High Co", canonical_name="high-co", score=80, priority="Pursue")
        high.observations.append(JobObservation(
            employer="High Co", title="Production Supervisor", location="La Crosse",
            industry="manufacturing", verified=True,
        ))
        queue = build_prospect_queue([low, high], minimum_score=50, priorities={"Pursue"})
        self.assertEqual([p.employer for p in queue], ["High Co"])
        self.assertEqual(queue[0].verified_opening_count, 1)
        self.assertIn("1 verified opening(s)", queue[0].reasons)

    def test_serialization_is_json_friendly(self):
        employer = Employer(name="Example", canonical_name="example", score=50, priority="Monitor")
        result = prospect_to_dict(build_prospect_queue([employer])[0])
        self.assertEqual(result["locations"], ())
        self.assertEqual(result["score"], 50)
        self.assertIsInstance(result["reasons"], tuple)


if __name__ == "__main__":
    unittest.main()
