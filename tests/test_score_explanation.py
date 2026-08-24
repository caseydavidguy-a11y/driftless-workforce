import unittest
from app.score_explanation import explain_score
from app.signals import HiringSignal

class ScoreExplanationTests(unittest.TestCase):
    def test_breakdown_reconciles_to_score(self):
        signals=[HiringSignal('leadership_new','high','New supervisor opening','Supervisor')]
        result=explain_score(55,signals,{'direction':'up','pct':100,'change':5,'days':7})
        self.assertEqual(result['score'],82)
        self.assertEqual(sum(x['points'] for x in result['items']),82)
        self.assertEqual(result['items'][0]['label'],'Base opportunity')

if __name__=='__main__':unittest.main()
