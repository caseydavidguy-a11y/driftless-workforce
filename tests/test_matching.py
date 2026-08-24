import unittest
from app.matching import match_candidate, rank_candidates

class MatchingTests(unittest.TestCase):
    def test_skill_location_match(self):
        c={'id':'c1','skills':'forklift welding','location':'La Crosse','available':True}
        s={'id':'s1','requirements':'forklift welding','location':'La Crosse'}
        m=match_candidate(c,s)
        self.assertEqual(m['score'],100); self.assertEqual(m['recommendation'],'Strong match')
    def test_rank(self):
        s={'id':'s1','requirements':'forklift','location':'La Crosse'}
        cs=[{'id':'a','skills':'forklift','location':'La Crosse'},{'id':'b','skills':'office','location':'La Crosse'}]
        self.assertEqual(rank_candidates(cs,s)[0]['candidate_id'],'a')

if __name__=='__main__':unittest.main()
