import unittest
from app.momentum import hiring_momentum, momentum_bonus, momentum_label

class MomentumTests(unittest.TestCase):
    def test_rising_momentum(self):
        s=[{'captured_at':'2026-08-20T10:00:00Z','employers':[{'opening_count':2}]},{'captured_at':'2026-08-24T10:00:00Z','employers':[{'opening_count':8}]}]
        m=hiring_momentum(s,7)
        self.assertEqual(m['direction'],'up'); self.assertEqual(m['change'],6); self.assertGreater(momentum_bonus(m),0); self.assertEqual(momentum_label(m),'Rising')

if __name__=='__main__': unittest.main()
