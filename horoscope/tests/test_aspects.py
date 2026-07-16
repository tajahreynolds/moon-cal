"""Tests for aspect detection and motion analysis."""

from django.test import SimpleTestCase

from horoscope.services import aspects as aspects_mod


def _natal_chart(moon_lon=0.0, moon_speed=12.0):
    return {
        "ascendant": {"lon": 0.0, "sign": "Aries", "sign_index": 0,
                      "deg_in_sign": 0.0},
        "planets": {
            "moon": {"lon": moon_lon, "speed": moon_speed},
        },
    }


def _transits(mars_lon, mars_speed):
    return {"mars": {"lon": mars_lon, "speed": mars_speed}}


class AspectDetectionTests(SimpleTestCase):
    def test_square_within_orb(self):
        # Mars 89.5 deg from natal Moon at 0 -> square (orb 0.5).
        natal = _natal_chart(moon_lon=0.0)
        transits = _transits(mars_lon=89.5, mars_speed=0.5)
        results = aspects_mod.find_aspects(transits, natal,
                                           transiting=("mars",),
                                           natal_points=("moon",))
        squares = [a for a in results if a["type"] == "square"]
        self.assertEqual(len(squares), 1)
        self.assertAlmostEqual(squares[0]["orb"], 0.5, places=1)

    def test_outside_orb_no_aspect(self):
        # 97.5 deg separation: 7.5 from square (orb 7) -> nothing.
        natal = _natal_chart(moon_lon=0.0)
        transits = _transits(mars_lon=97.5, mars_speed=0.5)
        results = aspects_mod.find_aspects(transits, natal,
                                           transiting=("mars",),
                                           natal_points=("moon",))
        self.assertEqual(results, [])

    def test_conjunction_wraparound(self):
        # Mars at 359 deg, natal Moon at 2 deg -> 3 deg apart -> conjunction.
        natal = _natal_chart(moon_lon=2.0)
        transits = _transits(mars_lon=359.0, mars_speed=0.5)
        results = aspects_mod.find_aspects(transits, natal,
                                           transiting=("mars",),
                                           natal_points=("moon",))
        self.assertTrue(any(a["type"] == "conjunction" for a in results))


class MotionAnalysisTests(SimpleTestCase):
    def test_applying_aspect_has_eta(self):
        # Mars at 88 deg moving forward toward exact square at 90.
        natal = _natal_chart(moon_lon=0.0)
        transits = _transits(mars_lon=88.0, mars_speed=0.5)
        a = aspects_mod.find_aspects(transits, natal, transiting=("mars",),
                                     natal_points=("moon",))[0]
        self.assertEqual(a["motion"], "applying")
        self.assertIsNotNone(a["days_to_exact"])
        self.assertIn("applying", a["text"])

    def test_separating_aspect_no_eta(self):
        # Mars at 92 deg moving forward, away from exact square at 90.
        natal = _natal_chart(moon_lon=0.0)
        transits = _transits(mars_lon=92.0, mars_speed=0.5)
        a = aspects_mod.find_aspects(transits, natal, transiting=("mars",),
                                     natal_points=("moon",))[0]
        self.assertEqual(a["motion"], "separating")
        self.assertIsNone(a["days_to_exact"])

    def test_honest_orb_language_no_false_exact(self):
        # 0.8 deg orb should NOT be called "exact".
        natal = _natal_chart(moon_lon=0.0)
        transits = _transits(mars_lon=89.2, mars_speed=0.5)
        a = aspects_mod.find_aspects(transits, natal, transiting=("mars",),
                                     natal_points=("moon",))[0]
        self.assertFalse(a["exact"])
        self.assertNotIn("exact now", a["text"])
        self.assertIn("within", a["text"])

    def test_true_exact_within_tenth_degree(self):
        natal = _natal_chart(moon_lon=0.0)
        transits = _transits(mars_lon=90.05, mars_speed=0.5)
        a = aspects_mod.find_aspects(transits, natal, transiting=("mars",),
                                     natal_points=("moon",))[0]
        self.assertTrue(a["exact"])
        self.assertIn("exact now", a["text"])


class CountAspectsTests(SimpleTestCase):
    def test_count_filters(self):
        aspects = [
            {"transiting": "mars", "natal": "sun", "category": "hard"},
            {"transiting": "saturn", "natal": "moon", "category": "hard"},
            {"transiting": "venus", "natal": "sun", "category": "soft"},
        ]
        n = aspects_mod.count_aspects(aspects, ("mars", "saturn"),
                                      ("sun", "moon"), ("hard",))
        self.assertEqual(n, 2)
