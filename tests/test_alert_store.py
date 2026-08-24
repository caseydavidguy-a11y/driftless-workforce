import json
import tempfile
import unittest
from pathlib import Path
from app.alert_store import serialize_signals, write_signals
from app.signals import HiringSignal

class AlertStoreTests(unittest.TestCase):
    def test_serializes_employer_and_signal(self):
        signal=HiringSignal('volume_increase','high','Openings increased','+3')
        data=serialize_signals({'Acme':[signal]})
        self.assertEqual(data['signals'][0]['employer'],'Acme')
        self.assertEqual(data['signals'][0]['severity'],'high')

    def test_writes_json(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'signals.json'
            write_signals(path, {'Acme':[HiringSignal('new_employer','high','New employer detected','new')]})
            self.assertEqual(json.loads(path.read_text())['signals'][0]['kind'],'new_employer')

if __name__=='__main__': unittest.main()
