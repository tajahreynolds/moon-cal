"""Natal chart computation.

Turns birth data (date, time, timezone, location) into a transparent chart:
every planet's longitude, sign, house and retrograde state, plus the
Ascendant and the chart ruler. Houses use whole-sign by default (house = the
sign's offset from the rising sign) which is deterministic and easy to verify;
Placidus is supported via the per-profile ``house_system`` flag.
"""

from __future__ import annotations

from datetime import date, datetime, time
from typing import Dict
from zoneinfo import ZoneInfo

from . import ephemeris

# Traditional (domicile) rulers. We use these rather than modern rulers because
# the classical rulers move fast enough that the "chart ruler" transit — which
# drives the Focus metric — actually changes day to day.
RULERS: Dict[str, str] = {
    "Aries": "mars",
    "Taurus": "venus",
    "Gemini": "mercury",
    "Cancer": "moon",
    "Leo": "sun",
    "Virgo": "mercury",
    "Libra": "venus",
    "Scorpio": "mars",
    "Sagittarius": "jupiter",
    "Capricorn": "saturn",
    "Aquarius": "saturn",
    "Pisces": "jupiter",
}


def whole_sign_house(planet_sign_index: int, asc_sign_index: int) -> int:
    """House number 1..12 under whole-sign houses."""
    return (planet_sign_index - asc_sign_index) % 12 + 1


def placidus_house(lon: float, cusps: list) -> int:
    """House number 1..12 by locating ``lon`` between Placidus cusps."""
    lon = lon % 360
    for i in range(12):
        start = cusps[i]
        end = cusps[(i + 1) % 12]
        span = (end - start) % 360
        offset = (lon - start) % 360
        if offset < span:
            return i + 1
    return 12  # pragma: no cover - defensive; cusps always cover the circle


def assign_house(lon: float, sign_idx: int, asc_sign_index: int, cusps: list,
                 house_system: str) -> int:
    if house_system == "P":
        return placidus_house(lon, cusps)
    return whole_sign_house(sign_idx, asc_sign_index)


def to_utc(birth_date: date, birth_time: time, tz_name: str) -> datetime:
    """Localize naive birth date/time in ``tz_name`` and convert to UTC.

    ``zoneinfo`` applies the historical DST rules for the birth date, so old
    birth times convert correctly.
    """
    local = datetime.combine(birth_date, birth_time, tzinfo=ZoneInfo(tz_name))
    return local.astimezone(ZoneInfo("UTC"))


def compute_natal_chart(birth_date: date, birth_time: time, tz_name: str,
                        lat: float, lon: float, house_system: str = "W") -> dict:
    """Compute the full natal chart as a JSON-serialisable dict."""
    dt_utc = to_utc(birth_date, birth_time, tz_name)
    hsys = b"P" if house_system == "P" else b"W"

    asc_lon, cusps = ephemeris.ascendant_and_cusps(dt_utc, lat, lon, hsys)
    asc_sign_index = ephemeris.sign_index(asc_lon)

    raw = ephemeris.planet_positions(dt_utc)
    planets: Dict[str, dict] = {}
    for name, p in raw.items():
        planets[name] = {
            **p,
            "house": assign_house(p["lon"], p["sign_index"], asc_sign_index,
                                  cusps, house_system),
        }

    asc_sign = ephemeris.SIGNS[asc_sign_index]
    return {
        "ascendant": {
            "lon": asc_lon,
            "sign": asc_sign,
            "sign_index": asc_sign_index,
            "deg_in_sign": ephemeris.deg_in_sign(asc_lon),
        },
        "house_cusps": cusps,
        "house_system": house_system,
        "chart_ruler": RULERS[asc_sign],
        "planets": planets,
    }
