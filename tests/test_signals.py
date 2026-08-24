import unittest
from app.models import Employer, JobObservation
from app.signals import compare_employer

class SignalTests(unittest.TestCase):
    def test_new_employer_signal(self):
        current=Employer('Acme','acme',observations=[JobObservation('Acme','Operator','La Crosse, WI','manufacturing')])
        self.assertEqual(compare_employer(current,None)[0].kind,'new_employer')

    def test_volume_increase(self):
        old=Employer('Acme','acme',observations=[JobObservation('Acme','Operator','La Crosse, WI','manufacturing')])
        current=Employer('Acme','acme',observations=[JobObservation('Acme','Operator','La Crosse, WI','manufacturing'),JobObservation('Acme','Supervisor','La Crosse, WI','leadership'),JobObservation('Acme','Technician','La Crosse, WI','skilled trades')])
        kinds=[s.kind for s in compare_employer(current,old)]
        self.assertIn('volume_increase',kinds)
        self.assertIn('leadership_new',kinds)

    def test_volume_decrease(self):
        old=Employer('Acme','acme',observations=[JobObservation('Acme','Operator','La Crosse, WI','manufacturing'),JobObservation('Acme','Technician','La Crosse, WI','skilled trades')])
        current=Employer('Acme','acme',observations=[JobObservation('Acme','Operator','La Crosse, WI','manufacturing')])
        self.assertEqual(compare_employer(current,old)[0].kind,'volume_decrease')

if __name__=='__main__': unittest.main()
