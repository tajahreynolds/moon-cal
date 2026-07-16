"""Aspect detection with motion analysis.

An aspect is a significant angular relationship between a transiting planet and
a natal point. Beyond the static angle we compute the *motion*: whether the
aspect is **applying** (tightening toward exact) or **separating** (loosening),
and an estimate of days until exact. This is the transparent, "show the raw
math" core of the product — we never claim "exactly" unless the orb is < 0.1 deg.
"""

from __future__ import annotations

from typing import Dict, List, Sequence

# aspect name -> (exact angle, orb allowance in degrees)
ASPECTS = {
    "conjunction": (0.0, 8.0),
    "sextile": (60.0, 5.0),
    "square": (90.0, 7.0),
    "trine": (120.0, 7.0),
    "opposition": (180.0, 8.0),
}
HARD = {"conjunction", "square", "opposition"}
SOFT = {"trine", "sextile"}

# Default sets used by the dashboard/forecast.
DEFAULT_TRANSITING = ("mars", "saturn", "jupiter", "venus", "sun", "moon")
DEFAULT_NATAL = ("sun", "moon", "mercury", "venus", "mars", "saturn", "ascendant")


def _sep(a: float, b: float) -> float:
    """Smallest angular separation 0..180 between two longitudes."""
    d = abs((a - b) % 360)
    return min(d, 360 - d)


def _natal_points(natal_chart: dict) -> Dict[str, dict]:
    """Map natal point name -> {lon, speed} (Ascendant treated as fixed)."""
    points: Dict[str, dict] = {}
    for name, p in natal_chart["planets"].items():
        points[name] = {"lon": p["lon"], "speed": p["speed"]}
    asc = natal_chart["ascendant"]
    points["ascendant"] = {"lon": asc["lon"], "speed": 0.0}
    return points


def _classify_motion(t_lon: float, t_speed: float, n_lon: float, angle: float):
    """Return (motion, days_to_exact) for a transiting body approaching an aspect.

    We measure the current separation vs the exact aspect angle, then nudge the
    transiting body forward by its daily speed and see whether the gap to exact
    shrinks (applying) or grows (separating). days_to_exact divides the current
    gap by the rate of change.
    """
    natal_points = (n_lon,)  # local helper readability
    gap_now = _sep(t_lon, n_lon) - angle
    # Position one day later (natal point is effectively fixed over a day).
    gap_next = _sep(t_lon + t_speed, n_lon) - angle
    closing_rate = abs(gap_now) - abs(gap_next)  # >0 means tightening
    if closing_rate > 0:
        motion = "applying"
    else:
        motion = "separating"
    days_to_exact = None
    if abs(closing_rate) > 1e-6 and motion == "applying":
        days_to_exact = abs(gap_now) / abs(closing_rate)
    return motion, days_to_exact


def _ordinal_deg(point: dict) -> int:
    return int(point["lon"] % 30)


def find_aspects(transits: Dict[str, dict], natal_chart: dict,
                 transiting: Sequence[str] = DEFAULT_TRANSITING,
                 natal_points: Sequence[str] = DEFAULT_NATAL) -> List[dict]:
    """Find all aspects between transiting planets and natal points.

    Each result is a dict with the raw math plus motion analysis and an
    honest, human-readable ``text`` string for the data drawer.
    """
    points = _natal_points(natal_chart)
    results: List[dict] = []
    for t_name in transiting:
        t = transits.get(t_name)
        if t is None:
            continue
        for n_name in natal_points:
            n = points.get(n_name)
            if n is None:
                continue
            separation = _sep(t["lon"], n["lon"])
            for asp_name, (angle, orb) in ASPECTS.items():
                delta = abs(separation - angle)
                if delta <= orb:
                    motion, dte = _classify_motion(t["lon"], t["speed"],
                                                   n["lon"], angle)
                    is_exact = delta < 0.1
                    results.append({
                        "transiting": t_name,
                        "natal": n_name,
                        "type": asp_name,
                        "category": "hard" if asp_name in HARD else "soft",
                        "angle": angle,
                        "orb": round(delta, 2),
                        "motion": motion,
                        "days_to_exact": round(dte, 1) if dte is not None else None,
                        "exact": is_exact,
                        "natal_deg": _ordinal_deg(n),
                        "text": _aspect_text(t_name, asp_name, n_name, delta,
                                             motion, dte, is_exact, _ordinal_deg(n)),
                    })
    # Tightest orbs first — the most relevant aspects lead.
    results.sort(key=lambda a: a["orb"])
    return results


def _aspect_text(t_name: str, asp_name: str, n_name: str, orb: float,
                 motion: str, dte, is_exact: bool, natal_deg: int) -> str:
    """Honest drawer string. No 'exactly' unless within 0.1 deg."""
    base = (f"Transiting {t_name.title()} {asp_name} natal "
            f"{n_name.title()} at {natal_deg}°")
    if is_exact:
        return base + " (exact now)."
    detail = f"within {orb:.1f}°, {motion}"
    if motion == "applying" and dte is not None:
        detail += f", exact in ~{_humanize_days(dte)}"
    return f"{base} ({detail})."


def _humanize_days(days: float) -> str:
    if days < 1:
        hours = max(1, round(days * 24))
        return f"{hours}h"
    return f"{round(days)}d"


def count_aspects(aspects: List[dict], transiting: Sequence[str],
                  natal: Sequence[str], categories: Sequence[str]) -> int:
    """Count aspects matching the given transiting/natal/category filters."""
    t, n, c = set(transiting), set(natal), set(categories)
    return sum(1 for a in aspects
               if a["transiting"] in t and a["natal"] in n and a["category"] in c)
