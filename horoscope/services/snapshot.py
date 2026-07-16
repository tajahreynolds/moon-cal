"""Snapshot orchestrator.

Views call only ``get_or_create_snapshot`` (one reading per profile per day,
cached) and ``flow_series`` (the 7-day forecast). Everything heavy — transit
positions, houses, aspects, scoring, directive text, next shift — happens here
once and is cached on the ``DailySnapshot`` row.
"""

from __future__ import annotations

from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from ..models import DailySnapshot, Profile
from . import aspects as aspects_mod
from . import scoring, textengine, transits


def _local_noon_utc(profile: Profile, local_date: date) -> datetime:
    """The UTC instant of local noon — a stable daily sampling point."""
    local = datetime.combine(local_date, time(12, 0),
                             tzinfo=ZoneInfo(profile.timezone))
    return local.astimezone(ZoneInfo("UTC"))


def build_payload(profile: Profile, local_date: date) -> dict:
    """Compute the full reading payload for a profile on a local date."""
    natal = profile.natal_chart
    dt_utc = _local_noon_utc(profile, local_date)

    raw_transits = transits.transit_positions(dt_utc)
    annotated = transits.add_transit_houses(raw_transits, natal)
    aspects = aspects_mod.find_aspects(annotated, natal)
    scores = scoring.compute_scores(natal, annotated, aspects)
    directives = [d._asdict() for d in
                  textengine.get_engine().directives(scores, annotated, natal)]
    shift = transits.next_shift(dt_utc)

    # Trim transits to the fields the UI needs (keeps payload small).
    transit_view = {
        name: {
            "sign": p["sign"], "house": p["house"],
            "deg_in_sign": round(p["deg_in_sign"], 2),
            "retrograde": p["retrograde"],
        }
        for name, p in annotated.items()
    }
    return {
        "scores": scores,
        "directives": directives,
        "transits": transit_view,
        "aspects": aspects,
        "next_shift": shift,
        "flow": scoring.flow_value(annotated, aspects),
    }


def get_or_create_snapshot(profile: Profile, local_date: date) -> DailySnapshot:
    """Return today's cached snapshot, computing and storing it if missing."""
    snap = DailySnapshot.objects.filter(profile=profile, date=local_date).first()
    if snap is not None:
        return snap
    payload = build_payload(profile, local_date)
    snap, _ = DailySnapshot.objects.get_or_create(
        profile=profile, date=local_date, defaults={"payload": payload})
    return snap


def flow_series(profile: Profile, start_date: date, days: int = 7) -> list:
    """Lightweight 7-day flow values for the forecast trend line.

    This intentionally does NOT persist a snapshot per day (only "today" is
    cached); it computes the flow value for each day on the fly.
    """
    natal = profile.natal_chart
    series = []
    for i in range(days):
        d = start_date + timedelta(days=i)
        dt_utc = _local_noon_utc(profile, d)
        annotated = transits.add_transit_houses(
            transits.transit_positions(dt_utc), natal)
        aspects = aspects_mod.find_aspects(annotated, natal)
        value = scoring.flow_value(annotated, aspects)
        # Dominant driver: the personal planet in the most extreme house tone.
        dominant = max(("moon", "sun", "mercury", "venus", "mars"),
                       key=lambda b: abs(scoring.tone(annotated[b]["house"])))
        series.append({
            "date": d.isoformat(),
            "weekday": d.strftime("%a"),
            "flow": value,
            "band": scoring.flow_band(value),
            "dominant": dominant,
            "dominant_house": annotated[dominant]["house"],
        })
    return series
