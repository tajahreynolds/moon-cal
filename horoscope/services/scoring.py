"""The scoring rubric — our heuristic "read" on top of the raw astronomy.

Everything here is interpretation, not fact: house tones, the Energy/Focus/
Friction levels, and the daily flow score are opinionated heuristics. The UI
labels them as "OUR READ" and links to the Methodology screen so users can
tell our interpretation apart from the computed positions/aspects.
"""

from __future__ import annotations

from typing import Dict, List

from . import aspects as aspects_mod

# A house's broad "tone": which life areas tend to feel supportive (+) vs.
# draining (-). 6th/12th are the classic rest/maintenance valleys; 1st/5th/9th
# are the high-alignment peaks called out in the product spec.
HOUSE_TONE = {1: +2, 2: +1, 3: +1, 4: 0, 5: +2, 6: -2, 7: +1,
              8: -1, 9: +2, 10: +1, 11: +1, 12: -2}

# One-word label per house for the Blueprint and directives.
HOUSE_LABELS = {
    1: "Identity", 2: "Resources", 3: "Signals", 4: "Base", 5: "Play",
    6: "Maintenance", 7: "Alliances", 8: "Debts", 9: "Expansion",
    10: "Career", 11: "Network", 12: "Subconscious",
}

_ENERGY_LEVELS = {3: "HIGH", 2: "MODERATE", 1: "LOW"}
_FOCUS_LEVELS = {3: "SHARP", 2: "STEADY", 1: "SCATTERED"}
_FRICTION_LEVELS = {3: "HIGH", 2: "MODERATE", 1: "LOW"}

# Friction colours map to the functional palette (red/yellow/green).
_FRICTION_COLOR = {3: "friction", 2: "standard", 1: "flow"}
_FLOW_COLOR = {3: "flow", 2: "standard", 1: "rest"}

_MAX_RAW = 23.0  # normalisation constant for the flow score


def _tone_to_bars(tone: int) -> int:
    """Map a house tone to a 1..3 bar count."""
    if tone >= 2:
        return 3
    if tone >= 0:
        return 2
    return 1


def tone(house: int) -> int:
    return HOUSE_TONE.get(house, 0)


def energy_score(moon_house: int) -> dict:
    bars = _tone_to_bars(tone(moon_house))
    return {"level": _ENERGY_LEVELS[bars], "bars": bars,
            "color": _FLOW_COLOR[bars], "house": moon_house}


def focus_score(ruler_house: int) -> dict:
    bars = _tone_to_bars(tone(ruler_house))
    return {"level": _FOCUS_LEVELS[bars], "bars": bars,
            "color": _FLOW_COLOR[bars], "house": ruler_house}


def friction_score(mars_house: int, aspects: List[dict]) -> dict:
    """Points-based friction from Mars's house and Mars hard aspects."""
    points = 0
    if mars_house in (6, 8, 12):
        points += 1
    for a in aspects:
        if a["transiting"] != "mars" or a["category"] != "hard":
            continue
        if a["natal"] not in ("sun", "moon", "mars", "saturn", "ascendant"):
            continue
        points += 2 if a["type"] in ("square", "opposition") else 1
    if points >= 3:
        bars = 3
    elif points >= 1:
        bars = 2
    else:
        bars = 1
    return {"level": _FRICTION_LEVELS[bars], "bars": bars,
            "color": _FRICTION_COLOR[bars], "points": points, "house": mars_house}


def compute_scores(natal_chart: dict, transits: Dict[str, dict],
                   aspects: List[dict]) -> dict:
    """Compute the three dashboard metrics from annotated transits.

    ``transits`` must already carry a ``house`` per planet (see
    ``transits.add_transit_houses``).
    """
    moon_house = transits["moon"]["house"]
    ruler = natal_chart["chart_ruler"]
    ruler_house = transits[ruler]["house"]
    mars_house = transits["mars"]["house"]
    return {
        "energy": energy_score(moon_house),
        "focus": focus_score(ruler_house),
        "friction": friction_score(mars_house, aspects),
    }


def flow_value(transits: Dict[str, dict], aspects: List[dict]) -> int:
    """Single 0..100 "Friction vs Flow" value for a day.

    Weighted sum of house tones for the personal planets, minus hard
    aspects from Mars/Saturn to luminaries/Ascendant, plus soft aspects from
    Jupiter/Venus. Normalised to 0..100 and clamped.
    """
    raw = (3.0 * tone(transits["moon"]["house"])
           + 2.0 * tone(transits["sun"]["house"])
           + 1.5 * tone(transits["mercury"]["house"])
           + 1.5 * tone(transits["venus"]["house"])
           + 2.0 * tone(transits["mars"]["house"]))
    raw -= 1.5 * aspects_mod.count_aspects(
        aspects, ("mars", "saturn"), ("sun", "moon", "ascendant"), ("hard",))
    raw += 1.0 * aspects_mod.count_aspects(
        aspects, ("jupiter", "venus"), ("sun", "moon", "ascendant"), ("soft",))
    value = round(50 + raw * 50 / _MAX_RAW)
    return max(0, min(100, value))


def flow_band(value: int) -> str:
    """Functional colour band for a flow value (peaks green, valleys blue)."""
    if value >= 60:
        return "flow"
    if value >= 40:
        return "standard"
    return "rest"
