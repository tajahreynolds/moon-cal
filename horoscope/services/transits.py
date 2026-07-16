"""Current planetary transits and the next major sky shift.

Transit positions reuse the ephemeris; house placement reuses the same
whole-sign / Placidus math as the natal chart. ``next_shift`` powers the
dashboard ticker: it finds the soonest *major* motion event — a planet
changing sign (ingress) or a planet turning retrograde/direct (station).
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Dict, Optional

from . import ephemeris
from .natal import assign_house

# Bodies whose ingresses/stations count as a "major shift" worth a countdown.
# The Moon moves fastest so its ingress is usually the nearest event.
_SHIFT_BODIES = ("moon", "sun", "mercury", "venus", "mars",
                 "jupiter", "saturn")
# Outer planets move slowly; their stations matter but ingresses are rare.
_STATION_BODIES = ("mercury", "venus", "mars", "jupiter", "saturn")


def transit_positions(dt_utc: datetime) -> Dict[str, dict]:
    """Current positions of all planets (same shape as natal planets)."""
    return ephemeris.planet_positions(dt_utc)


def transit_house(transit_lon: float, natal_chart: dict) -> int:
    """House occupied by a transiting longitude in the user's chart."""
    asc_sign_index = natal_chart["ascendant"]["sign_index"]
    sign_idx = ephemeris.sign_index(transit_lon)
    return assign_house(transit_lon, sign_idx, asc_sign_index,
                        natal_chart["house_cusps"],
                        natal_chart.get("house_system", "W"))


def add_transit_houses(transits: Dict[str, dict], natal_chart: dict) -> Dict[str, dict]:
    """Annotate each transiting planet with its current house."""
    return {name: {**p, "house": transit_house(p["lon"], natal_chart)}
            for name, p in transits.items()}


def _body_lon(dt_utc: datetime, name: str) -> float:
    return ephemeris.planet_positions(dt_utc)[name]["lon"]


def _next_ingress(dt_utc: datetime, name: str, horizon_hours: int) -> Optional[dict]:
    """Find the next sign change for ``name`` within the horizon.

    Coarse hourly stepping (no body crosses a 30 deg boundary in under an hour)
    then bisection to ~1 minute precision.
    """
    start_lon = _body_lon(dt_utc, name)
    start_sign = ephemeris.sign_index(start_lon)
    step = timedelta(hours=1)
    t_prev = dt_utc
    for h in range(1, horizon_hours + 1):
        t = dt_utc + step * h
        sign = ephemeris.sign_index(_body_lon(t, name))
        if sign != start_sign:
            at = _bisect_event(t_prev, t, name, _crossed_sign(start_sign))
            new_sign = ephemeris.SIGNS[(start_sign + 1) % 12]
            return {"kind": "ingress", "body": name, "sign": new_sign, "at_utc": at}
        t_prev = t
    return None


def _crossed_sign(start_sign: int):
    def predicate(t: datetime, name: str) -> bool:
        return ephemeris.sign_index(_body_lon(t, name)) != start_sign
    return predicate


def _next_station(dt_utc: datetime, name: str, horizon_hours: int) -> Optional[dict]:
    """Find the next retrograde/direct station (speed sign change)."""
    start_speed = ephemeris.planet_positions(dt_utc)[name]["speed"]
    start_sign = start_speed < 0
    step = timedelta(hours=6)
    steps = horizon_hours // 6
    t_prev = dt_utc
    for h in range(1, steps + 1):
        t = dt_utc + step * h
        retro = ephemeris.planet_positions(t)[name]["speed"] < 0
        if retro != start_sign:
            at = _bisect_event(t_prev, t, name, _changed_direction(start_sign))
            kind_word = "turns retrograde" if retro else "turns direct"
            return {"kind": "station", "body": name, "phrase": kind_word, "at_utc": at}
        t_prev = t
    return None


def _changed_direction(start_retro: bool):
    def predicate(t: datetime, name: str) -> bool:
        return (ephemeris.planet_positions(t)[name]["speed"] < 0) != start_retro
    return predicate


def _bisect_event(lo: datetime, hi: datetime, name: str, predicate) -> datetime:
    """Bisect [lo, hi] to ~1 minute where ``predicate`` flips False->True."""
    while (hi - lo) > timedelta(minutes=1):
        mid = lo + (hi - lo) / 2
        if predicate(mid, name):
            hi = mid
        else:
            lo = mid
    return hi.astimezone(timezone.utc)


def next_shift(dt_utc: datetime, horizon_hours: int = 72) -> Optional[dict]:
    """Soonest major shift: nearest planetary ingress or retrograde station.

    Returns ``{kind, body, label, at_utc, seconds_remaining}`` or ``None`` if
    nothing notable happens within the horizon.
    """
    candidates = []
    for name in _SHIFT_BODIES:
        ing = _next_ingress(dt_utc, name, horizon_hours)
        if ing:
            candidates.append(ing)
    for name in _STATION_BODIES:
        st = _next_station(dt_utc, name, horizon_hours)
        if st:
            candidates.append(st)
    if not candidates:
        return None
    soonest = min(candidates, key=lambda e: e["at_utc"])
    if soonest["kind"] == "ingress":
        label = f"{soonest['body'].title()} enters {soonest['sign']}"
    else:
        label = f"{soonest['body'].title()} {soonest['phrase']}"
    seconds = max(0, int((soonest["at_utc"] - dt_utc).total_seconds()))
    return {
        "kind": soonest["kind"],
        "body": soonest["body"],
        "label": label,
        "at_utc": soonest["at_utc"].isoformat(),
        "seconds_remaining": seconds,
    }
