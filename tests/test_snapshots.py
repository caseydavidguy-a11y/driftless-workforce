import tempfile
import unittest
from pathlib import Path
from app.models import Employer, JobObservation
from app.snapshots import snapshot_record, write_snapshot, read_snapshot
from app.change_report import compare_snapshots

class SnapshotTests(unittest.TestCase):
    def employers(self, count):
        titles=['Operator','Technician','Supervisor'][:count]
        return [Employer('Acme','acme',observations=[JobObservation('Acme',t,'La Crosse, WI','manufacturing') for t in titles])]

    def test_snapshot_round_trip(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'snapshot.json'
            write_snapshot(p,self.employers(2),'2026-08-23T10:00:00+00:00')
            data=read_snapshot(p)
            self.assertEqual(data['captured_at'],'2026-08-23T10:00:00+00:00')
            self.assertEqual(data['employers'][0]['opening_count'],2)

    def test_change_report_detects_new_opening(self):
        old=snapshot_record(self.employers(1),'2026-08-23T10:00:00+00:00')
        new=snapshot_record(self.employers(3),'2026-08-24T10:00:00+00:00')
        report=compare_snapshots(old,new)
        kinds=[s['kind'] for c in report['changes'] for s in c['signals']]
        self.assertIn('volume_increase',kinds)

if __name__=='__main__': unittest.main()
