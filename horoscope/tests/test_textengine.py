"""Tests for the pluggable text engine and the UX-rule validator."""

from django.test import SimpleTestCase

from horoscope.services import textengine
from horoscope.services.textengine import (
    ClaudeEngine,
    Directive,
    RuleBasedEngine,
    validate,
)


def _transits():
    return {b: {"sign": "Taurus", "house": 6, "deg_in_sign": 10.0,
                "retrograde": False}
            for b in ("sun", "moon", "mercury", "venus", "mars",
                      "jupiter", "saturn")}


class ValidateTests(SimpleTestCase):
    def test_rejects_overlong_sentence(self):
        d = Directive("energy", "battery", "X", "y" * 91 + ".", "Go.")
        with self.assertRaises(ValueError):
            validate(d)

    def test_rejects_multiline(self):
        d = Directive("energy", "battery", "X", "line one.\nline two.", "Go.")
        with self.assertRaises(ValueError):
            validate(d)

    def test_requires_period(self):
        with self.assertRaises(ValueError):
            validate(Directive("energy", "battery", "X", "no period", "Go."))

    def test_accepts_valid(self):
        d = Directive("energy", "battery", "X", "Moon is in your 6th House.", "Rest.")
        self.assertIs(validate(d), d)


class RuleBasedEngineTests(SimpleTestCase):
    def setUp(self):
        self.natal = {"chart_ruler": "mercury"}
        self.scores = {
            "energy": {"level": "LOW", "bars": 1, "house": 12},
            "focus": {"level": "SHARP", "bars": 3, "house": 5},
            "friction": {"level": "HIGH", "bars": 3, "house": 7, "points": 3},
        }

    def test_produces_three_valid_directives(self):
        directives = RuleBasedEngine().directives(self.scores, _transits(), self.natal)
        self.assertEqual(len(directives), 3)
        metrics = {d.metric for d in directives}
        self.assertEqual(metrics, {"energy", "focus", "friction"})
        for d in directives:
            validate(d)  # must not raise

    def test_sentence_cites_house_and_sign(self):
        directives = RuleBasedEngine().directives(self.scores, _transits(), self.natal)
        energy = next(d for d in directives if d.metric == "energy")
        self.assertIn("House", energy.sentence)
        self.assertIn("Taurus", energy.sentence)

    def test_retrograde_surfaced_in_sentence(self):
        transits = _transits()
        transits["mercury"]["retrograde"] = True
        directives = RuleBasedEngine().directives(self.scores, transits, self.natal)
        focus = next(d for d in directives if d.metric == "focus")
        self.assertIn("retrograde", focus.sentence)


class ClaudeEngineTests(SimpleTestCase):
    def test_stub_raises(self):
        with self.assertRaises(NotImplementedError):
            ClaudeEngine().directives({}, {}, {})


class GetEngineTests(SimpleTestCase):
    def test_default_engine_is_rule_based(self):
        self.assertIsInstance(textengine.get_engine(), RuleBasedEngine)
