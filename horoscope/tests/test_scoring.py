"""Tests for the Energy/Focus/Friction rubric and flow score."""

from django.test import SimpleTestCase

from horoscope.services import scoring


def _transits(**houses):
    """Build a minimal annotated-transits dict with given houses."""
    base = {b: {"house": 4, "sign": "Aries", "deg_in_sign": 0.0,
                "retrograde": False, "speed": 1.0, "lon": 0.0}
            for b in ("sun", "moon", "mercury", "venus", "mars",
                      "jupiter", "saturn", "uranus", "neptune", "pluto")}
    for body, house in houses.items():
        base[body]["house"] = house
    return base


class EnergyTests(SimpleTestCase):
    def test_moon_in_12th_is_low(self):
        s = scoring.energy_score(12)
        self.assertEqual(s["level"], "LOW")
        self.assertEqual(s["bars"], 1)
        self.assertEqual(s["color"], "rest")

    def test_moon_in_1st_is_high(self):
        s = scoring.energy_score(1)
        self.assertEqual(s["level"], "HIGH")
        self.assertEqual(s["bars"], 3)

    def test_moon_in_4th_is_moderate(self):
        self.assertEqual(scoring.energy_score(4)["level"], "MODERATE")


class FrictionTests(SimpleTestCase):
    def test_mars_in_6th_plus_hard_square_is_high(self):
        aspects = [{"transiting": "mars", "natal": "moon", "type": "square",
                    "category": "hard"}]
        s = scoring.friction_score(6, aspects)
        self.assertEqual(s["points"], 3)  # 1 (house) + 2 (square)
        self.assertEqual(s["level"], "HIGH")
        self.assertEqual(s["color"], "friction")

    def test_no_mars_pressure_is_low(self):
        s = scoring.friction_score(1, [])
        self.assertEqual(s["points"], 0)
        self.assertEqual(s["level"], "LOW")
        self.assertEqual(s["color"], "flow")

    def test_non_mars_aspect_ignored(self):
        aspects = [{"transiting": "saturn", "natal": "moon", "type": "square",
                    "category": "hard"}]
        self.assertEqual(scoring.friction_score(1, aspects)["points"], 0)


class FocusTests(SimpleTestCase):
    def test_ruler_in_10th_is_steady(self):
        # 10th house tone is +1 -> 2 bars -> STEADY
        self.assertEqual(scoring.focus_score(10)["level"], "STEADY")

    def test_ruler_in_5th_is_sharp(self):
        self.assertEqual(scoring.focus_score(5)["level"], "SHARP")


class ComputeScoresTests(SimpleTestCase):
    def test_uses_chart_ruler_for_focus(self):
        natal = {"chart_ruler": "mercury"}
        transits = _transits(moon=12, mercury=1, mars=7)
        scores = scoring.compute_scores(natal, transits, [])
        self.assertEqual(scores["energy"]["level"], "LOW")    # moon 12th
        self.assertEqual(scores["focus"]["level"], "SHARP")   # mercury 1st
        self.assertEqual(scores["friction"]["house"], 7)


class FlowTests(SimpleTestCase):
    def test_flow_clamped_and_normalised(self):
        # All personal planets in peak houses -> high flow, clamped <= 100.
        peak = _transits(moon=1, sun=5, mercury=9, venus=1, mars=5)
        self.assertLessEqual(scoring.flow_value(peak, []), 100)
        self.assertGreater(scoring.flow_value(peak, []), 60)

    def test_valley_houses_lower_flow(self):
        valley = _transits(moon=12, sun=6, mercury=12, venus=6, mars=6)
        self.assertLess(scoring.flow_value(valley, []), 40)

    def test_flow_band_thresholds(self):
        self.assertEqual(scoring.flow_band(75), "flow")
        self.assertEqual(scoring.flow_band(50), "standard")
        self.assertEqual(scoring.flow_band(20), "rest")
