"""Tests for nara_exporter parsing and normalization.

Run with: python -m pytest tests/  (or: python -m unittest discover tests)
"""

from __future__ import annotations

import unittest
from pathlib import Path

from nara_exporter.normalize import normalize_rows
from nara_exporter.parser import read_raw_rows

FIXTURE = Path(__file__).parent / "fixtures" / "sample_export.csv"


class TestNormalize(unittest.TestCase):
    def setUp(self):
        rows = read_raw_rows(FIXTURE)
        self.events = list(normalize_rows(rows))
        self.by_type = {e.event_type: e for e in self.events}

    def test_all_rows_parsed(self):
        self.assertEqual(len(self.events), 8)

    def test_breastfeed_duration_sums_sides(self):
        event = self.by_type["breastfeeding"]
        self.assertEqual(event.breastfeed_left_seconds, 300)
        self.assertEqual(event.breastfeed_right_seconds, 280)
        self.assertEqual(event.duration_seconds, 580)

    def test_sleep_duration_and_end_time(self):
        event = self.by_type["sleep"]
        self.assertEqual(event.duration_seconds, 3600)
        self.assertEqual(event.end_time, "2026-09-20 10:15:00")

    def test_diaper_type(self):
        event = self.by_type["diaper"]
        self.assertEqual(event.diaper_type, "Wet")

    def test_bottle_feed_volume_normalized_to_ml(self):
        event = self.by_type["bottle_feeding"]
        self.assertEqual(event.bottle_type, "Formula")
        self.assertEqual(event.bottle_volume_ml, 120.0)

    def test_pump_volumes(self):
        event = self.by_type["pumping"]
        self.assertEqual(event.pump_left_ml, 60.0)
        self.assertEqual(event.pump_right_ml, 70.0)
        self.assertEqual(event.pump_total_ml, 130.0)

    def test_growth_units_normalized(self):
        event = self.by_type["growth"]
        self.assertEqual(event.growth_weight_kg, 4.2)
        self.assertEqual(event.growth_height_cm, 55.0)
        self.assertEqual(event.growth_head_cm, 38.0)

    def test_profile_row(self):
        event = self.by_type["profile"]
        self.assertEqual(event.profile_sex, "FEMALE")
        self.assertEqual(event.profile_birth_date, "2026-01-01")

    def test_unknown_type_is_preserved_not_dropped(self):
        unknown_events = [e for e in self.events if e.event_type == "unknown"]
        self.assertEqual(len(unknown_events), 1)
        event = unknown_events[0]
        self.assertEqual(event.raw_type, "Milestone")
        self.assertEqual(event.note, "First smile!")


class TestUnitConversion(unittest.TestCase):
    def test_oz_to_ml(self):
        from nara_exporter.schema import volume_to_ml

        self.assertAlmostEqual(volume_to_ml("4", "OZ"), 118.294, places=2)

    def test_lb_to_kg(self):
        from nara_exporter.schema import weight_to_kg

        self.assertAlmostEqual(weight_to_kg("10", "LB"), 4.53592, places=4)

    def test_unknown_unit_passthrough(self):
        from nara_exporter.schema import length_to_cm

        self.assertEqual(length_to_cm("20", "FURLONGS"), 20.0)

    def test_empty_value_returns_none(self):
        from nara_exporter.schema import volume_to_ml

        self.assertIsNone(volume_to_ml("", "ML"))
        self.assertIsNone(volume_to_ml(None, "ML"))


if __name__ == "__main__":
    unittest.main()
