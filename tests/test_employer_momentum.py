import unittest
from app.employer_momentum import employer_momentum, employer_momentum_bonus

class EmployerMomentumTests(unittest.TestCase):
    def test_company_specific_momentum(self):
        snapshots=[
          {'captured_at':'2026-08-20T10:00:00Z','employers':[{'slug':'acme','opening_count':2},{'slug':'other','opening_count':20}]},
          {'captured_at':'2026-08-24T10:00:00Z','employers':[{'slug':'acme','opening_count':8},{'slug':'other','opening_count':18}]}
        ]
        m=employer_momentum(snapshots,'acme',7)
        self.assertEqual(m['change'],6); self.assertEqual(m['direction'],'up'); self.assertGreater(employer_momentum_bonus(m),0)

if __name__=='__main__':unittest.main()
