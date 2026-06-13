"""Thin wrapper around the Swiss Ephemeris (pyswisseph).

This is the ONLY module in the project that imports ``swisseph``. Everything
else works with plain dicts/floats so the astrology logic stays testable and
the ephemeris backend stays swappable.

We use the built-in **Moshier** analytical ephemeris (``swe.FLG_MOSEPH``),
which needs no external data files and works fully offline. Precision is far
beyond astrological need (sub-arcsecond for planets). We never call
``swe.set_ephe_path`` so no ``.se1`` files are ever required.

Zodiac is **tropical** and house system defaults to **whole-sign** — both are
disclosed to the user on the Methodology screen.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict

import swisseph as swe

# Moshier ephemeris + planetary speed (speed lets us detect retrograde motion).
_FLAGS = swe.FLG_MOSEPH | swe.FLG_SPEED

# The ten bodies a Western chart cares about, in conventional order.
PLANETS: Dict[str, int] = {
    "sun": swe.SUN,
    "moon": swe.MOON,
    "mercury": swe.MERCURY,
    "venus": swe.VENUS,
    "mars": swe.MARS,
    "jupiter": swe.JUPITER,
    "saturn": swe.SATURN,
    "uranus": swe.URANUS,
    "neptune": swe.NEPTUNE,
    "pluto": swe.PLUTO,
}

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]


def sign_index(lon: float) -> int:
    """Zodiac sign index 0..11 (0 = Aries) for an ecliptic longitude."""
    return int(lon % 360 // 30)


def sign_name(lon: float) -> str:
    return SIGNS[sign_index(lon)]


def deg_in_sign(lon: float) -> float:
    """Degrees 0..30 within the body's current sign."""
    return lon % 30


def to_julian_day(dt_utc: datetime) -> float:
    """Convert a timezone-aware UTC datetime to a Julian Day (UT)."""
    if dt_utc.tzinfo is None:
        raise ValueError("datetime must be timezone-aware (UTC)")
    dt = dt_utc.astimezone(timezone.utc)
    hour = dt.hour + dt.minute / 60.0 + dt.second / 3600.0
    return swe.julday(dt.year, dt.month, dt.day, hour)


def planet_positions(dt_utc: datetime) -> Dict[str, dict]:
    """Compute ecliptic longitude, speed and retrograde flag for all planets.

    Returns ``{name: {"lon", "sign", "sign_index", "deg_in_sign", "speed",
    "retrograde"}}``. ``retrograde`` is ``True`` when apparent longitudinal
    speed is negative — the raw, transparent definition of retrograde motion.
    """
    jd = to_julian_day(dt_utc)
    out: Dict[str, dict] = {}
    for name, body in PLANETS.items():
        values, _flags = swe.calc_ut(jd, body, _FLAGS)
        lon = values[0] % 360
        speed = values[3]
        out[name] = {
            "lon": lon,
            "sign": SIGNS[sign_index(lon)],
            "sign_index": sign_index(lon),
            "deg_in_sign": deg_in_sign(lon),
            "speed": speed,
            "retrograde": speed < 0,
        }
    return out


def ascendant_and_cusps(dt_utc: datetime, lat: float, lon: float, hsys: bytes = b"W"):
    """Return ``(ascendant_longitude, [12 house cusp longitudes])``.

    ``hsys`` is a Swiss Ephemeris house-system code; ``b"W"`` is whole-sign,
    ``b"P"`` is Placidus. House calculation needs no data files.
    """
    jd = to_julian_day(dt_utc)
    cusps, ascmc = swe.houses(jd, lat, lon, hsys)
    ascendant = ascmc[0] % 360
    return ascendant, [c % 360 for c in cusps]
