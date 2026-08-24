import tempfile
import unittest
from pathlib import Path
from scripts.validate_outputs import REQUIRED_OPPORTUNITY

class ValidationContractTests(unittest.TestCase):
    def test_opportunity_contract_is_explicit(self):
        required={'employer','slug','score','priority','opening_count','verified_opening_count','locations','industries','score_breakdown','score_policy_version'}
        self.assertEqual(REQUIRED_OPPORTUNITY, required)

if __name__=='__main__': unittest.main()
