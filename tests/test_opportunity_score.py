import unittest
from app.opportunity_score import calculate_opportunity_score, priority_for_score
from app.signals import HiringSignal

class OpportunityScoreTests(unittest.TestCase):
    def test_score_combines_signal_and_momentum(self):
        signals=[HiringSignal('leadership_new','high','New supervisor opening','Supervisor')]
        momentum={'direction':'up','pct':100,'change':5}
        score=calculate_opportunity_score(55,signals,momentum)
        self.assertEqual(score,82)
        self.assertEqual(priority_for_score(score),'Pursue')

    def test_score_is_bounded(self):
        signals=[HiringSignal('leadership_new','high','x','x')]*5
        momentum={'direction':'up','pct':500,'change':20}
        self.assertEqual(calculate_opportunity_score(98,signals,momentum),100)

if __name__=='__main__': unittest.main()
