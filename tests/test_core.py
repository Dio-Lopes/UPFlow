import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
import json

from upflow.settings import Venue, load_venues, topic
from upflow.publisher import make_reading

class CoreTests(unittest.TestCase):
    def setUp(self):
        self.v = Venue('feup', 'bar_minas', 'Bar de Minas', 100, 25)

    def test_topic(self):
        self.assertEqual(topic('feup', 'bar_minas', 'raw', 'reading'), 'upflow/v1/feup/bar_minas/raw/reading')
        with self.assertRaises(ValueError):
            topic('feup', '#', 'raw', 'reading')

    def test_reading_contract(self):
        d = make_reading(self.v, 76)
        self.assertEqual(d['occupied'], 76)
        self.assertEqual(d['capacity'], 100)
        self.assertTrue(d['observed_at'].endswith('Z'))

    def test_reject_out_of_range(self):
        with self.assertRaises(ValueError):
            make_reading(self.v, 101)
        with self.assertRaises(ValueError):
            make_reading(self.v, -1)

    def test_duplicate_venues(self):
        with TemporaryDirectory() as folder:
            p = Path(folder)/'venues.json'
            record = vars(self.v)
            p.write_text(json.dumps([record, record]), encoding='utf-8')
            with self.assertRaises(ValueError):
                load_venues(p)

if __name__ == '__main__':
    unittest.main()
