"""Tests for natal chart computation.

Uses a fixed birth instant (2000-01-01 12:00 UTC at Greenwich) so the computed
positions are deterministic. A few longitudes are pinned as regression values
(tolerance 0.01 deg) to catch accidental changes to the ephemeris path.
"""

from datetime import date, time

from django.test import SimpleTestCase

from horoscope.services import ephemeris
from horoscope.services.natal import (
    RULERS,
    compute_natal_chart,
    placidus_house,
    whole_sign_house,
)

BIRTH = dict(birth_date=date(2000, 1, 1), birth_time=time(12, 0),
             tz_name="UTC", lat=51.48, lon=0.0)


class NatalChartTests(SimpleTestCase):
    def setUp(self):
        self.chart = compute_natal_chart(**BIRTH, house_system="W")

    def test_all_ten_planets_present(self):
        self.assertEqual(set(self.chart["planets"]), set(ephemeris.PLANETS))

    def test_longitudes_in_range(self):
        for p in self.chart["planets"].values():
            self.assertGreaterEqual(p["lon"], 0.0)
            self.assertLess(p["lon"], 360.0)
            self.assertIn(p["house"], range(1, 13))

    def test_sun_in_capricorn(self):
        # The Sun is in Capricorn all day on 2000-01-01.
        self.assertEqual(self.chart["planets"]["sun"]["sign"], "Capricorn")

    def test_regression_longitudes(self):
        # Pinned Moshier values; recompute only if intentionally changing ephemeris.
        self.assertAlmostEqual(self.chart["planets"]["sun"]["lon"], 280.3689, places=2)
        self.assertAlmostEqual(self.chart["planets"]["moon"]["lon"], 223.3238, places=2)
        self.assertAlmostEqual(self.chart["ascendant"]["lon"], 24.2682, places=2)

    def test_chart_ruler_matches_ascendant(self):
        asc_sign = self.chart["ascendant"]["sign"]
        self.assertEqual(self.chart["chart_ruler"], RULERS[asc_sign])

    def test_retrograde_flag_present_and_boolean(self):
        for p in self.chart["planets"].values():
            self.assertIsInstance(p["retrograde"], bool)
            # retrograde iff speed negative — the raw definition
            self.assertEqual(p["retrograde"], p["speed"] < 0)

    def test_deterministic(self):
        again = compute_natal_chart(**BIRTH, house_system="W")
        self.assertEqual(again["planets"]["mars"]["lon"],
                         self.chart["planets"]["mars"]["lon"])

    def test_whole_sign_house_math(self):
        # Asc in Aries (index 0): a planet in Aries is house 1, Taurus house 2.
        self.assertEqual(whole_sign_house(0, 0), 1)
        self.assertEqual(whole_sign_house(1, 0), 2)
        self.assertEqual(whole_sign_house(11, 0), 12)
        # Asc in Capricorn (index 9): Capricorn planet is house 1.
        self.assertEqual(whole_sign_house(9, 9), 1)
        self.assertEqual(whole_sign_house(10, 9), 2)


class PlacidusFallbackTests(SimpleTestCase):
    def test_placidus_house_locates_longitude(self):
        chart = compute_natal_chart(**BIRTH, house_system="P")
        cusps = chart["house_cusps"]
        # Each planet's stored house must agree with a fresh lookup.
        for p in chart["planets"].values():
            self.assertEqual(placidus_house(p["lon"], cusps), p["house"])
