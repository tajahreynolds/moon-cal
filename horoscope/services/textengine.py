"""Pluggable text engine for daily directives.

A directive is one icon + one short label + one factual sentence (citing the
transit) + one imperative. The rule-based engine ships now; a Claude-backed
engine is stubbed for later. Any engine's output must pass ``validate`` — the
single source of truth for the "no scrolling text blocks" UX rule.
"""

from __future__ import annotations

from typing import List, NamedTuple, Protocol

from django.conf import settings
from django.utils.module_loading import import_string

from .scoring import HOUSE_LABELS

MAX_LEN = 90  # one card line; longer than this needs a scrollbar -> rejected


class Directive(NamedTuple):
    metric: str       # "energy" | "focus" | "friction"
    icon: str         # icon key for the template (battery/brain/shield)
    label: str        # e.g. "ENERGY STATUS: LOW"
    sentence: str     # factual: cites the transit
    imperative: str   # actionable: what to do


class TextEngine(Protocol):
    def directives(self, scores: dict, transits: dict,
                   natal_chart: dict) -> List[Directive]:
        ...


def _ordinal(n: int) -> str:
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def validate(directive: Directive) -> Directive:
    """Enforce the glanceable-card UX rule. Raises ValueError on violation."""
    for field in ("sentence", "imperative"):
        text = getattr(directive, field)
        if not text:
            raise ValueError(f"{directive.metric}.{field} is empty")
        if len(text) > MAX_LEN:
            raise ValueError(
                f"{directive.metric}.{field} too long ({len(text)} > {MAX_LEN})")
        if "\n" in text:
            raise ValueError(f"{directive.metric}.{field} must be a single line")
        if not text.rstrip().endswith("."):
            raise ValueError(f"{directive.metric}.{field} must end with a period")
    return directive


# Imperatives keyed by (metric, level). Short, verb-first, no fluff.
_IMPERATIVES = {
    ("energy", "HIGH"): "Spend it on the work that matters.",
    ("energy", "MODERATE"): "Pace yourself and protect the essentials.",
    ("energy", "LOW"): "Protect your time and decline optional tasks.",
    ("focus", "SHARP"): "Pitch, write, or have the hard conversation.",
    ("focus", "STEADY"): "Handle routine work; save big calls for later.",
    ("focus", "SCATTERED"): "Avoid big decisions; capture notes instead.",
    ("friction", "HIGH"): "Walk away from bait and avoid arguments.",
    ("friction", "MODERATE"): "Stay measured; pick your battles.",
    ("friction", "LOW"): "Push forward; the path is clear.",
}


class RuleBasedEngine:
    """Deterministic directive text built directly from the transit data."""

    def directives(self, scores: dict, transits: dict,
                   natal_chart: dict) -> List[Directive]:
        return [
            validate(self._energy(scores, transits)),
            validate(self._focus(scores, transits, natal_chart)),
            validate(self._friction(scores, transits)),
        ]

    def _house_phrase(self, body: str, transits: dict) -> str:
        p = transits[body]
        retro = " retrograde" if p.get("retrograde") else ""
        return f"{p['sign']}{retro}"

    def _energy(self, scores, transits) -> Directive:
        s = scores["energy"]
        house = s["house"]
        sign = self._house_phrase("moon", transits)
        sentence = f"Moon is in your {_ordinal(house)} House ({sign})."
        return Directive("energy", "battery", f"ENERGY STATUS: {s['level']}",
                         sentence, _IMPERATIVES[("energy", s["level"])])

    def _focus(self, scores, transits, natal_chart) -> Directive:
        s = scores["focus"]
        ruler = natal_chart["chart_ruler"]
        house = s["house"]
        sign = self._house_phrase(ruler, transits)
        sentence = (f"{ruler.title()}, your ruler, is in your "
                    f"{_ordinal(house)} House ({sign}).")
        if len(sentence) > MAX_LEN:  # fall back to a terser phrasing
            sentence = f"{ruler.title()} is in your {_ordinal(house)} House ({sign})."
        return Directive("focus", "brain", f"MENTAL FOCUS: {s['level']}",
                         sentence, _IMPERATIVES[("focus", s["level"])])

    def _friction(self, scores, transits) -> Directive:
        s = scores["friction"]
        house = s["house"]
        sign = self._house_phrase("mars", transits)
        sentence = f"Mars is hitting your {_ordinal(house)} House ({sign})."
        return Directive("friction", "shield", f"FRICTION WARN: {s['level']}",
                         sentence, _IMPERATIVES[("friction", s["level"])])


class ClaudeEngine:
    """Stub for a future Claude-backed nightly text generator.

    Intended contract: once per night, feed the transit JSON (scores +
    cited transits) to Claude with a strict prompt that mirrors ``validate``'s
    constraints (one factual sentence + one imperative, each <= 90 chars), then
    cache the result on the DailySnapshot. Not implemented in v1.
    """

    def directives(self, scores: dict, transits: dict,
                   natal_chart: dict) -> List[Directive]:
        raise NotImplementedError(
            "ClaudeEngine is a stub; set HOROSCOPE_TEXT_ENGINE to "
            "RuleBasedEngine. See docstring for the intended prompt contract.")


def get_engine() -> TextEngine:
    """Instantiate the engine named by ``settings.HOROSCOPE_TEXT_ENGINE``."""
    dotted = getattr(settings, "HOROSCOPE_TEXT_ENGINE",
                     "horoscope.services.textengine.RuleBasedEngine")
    return import_string(dotted)()
