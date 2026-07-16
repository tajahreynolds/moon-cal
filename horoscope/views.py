"""Views for the three screens, onboarding, JSON endpoints and PWA assets."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from django.http import Http404, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import FormView, TemplateView

from .forms import OnboardingForm
from .models import Profile
from .services import cities, snapshot
from .services.natal import compute_natal_chart
from .services.scoring import HOUSE_LABELS


def _today_for(profile: Profile) -> date:
    """Current local date in the profile's timezone."""
    return datetime.now(ZoneInfo(profile.timezone)).date()


class ProfileRequiredMixin:
    """Resolve the session's Profile or redirect to onboarding."""

    def dispatch(self, request, *args, **kwargs):
        key = request.session.session_key
        profile = None
        if key:
            profile = Profile.objects.filter(session_key=key).first()
        if profile is None:
            return redirect("horoscope:onboarding")
        self.profile = profile
        return super().dispatch(request, *args, **kwargs)


class DashboardView(ProfileRequiredMixin, TemplateView):
    """Screen 1 — the Tactical Dashboard."""

    template_name = "horoscope/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        today = _today_for(self.profile)
        snap = snapshot.get_or_create_snapshot(self.profile, today)
        payload = snap.payload
        ctx.update({
            "today": today,
            "scores": payload["scores"],
            "directives": payload["directives"],
            "next_shift": payload["next_shift"],
            "flow": payload["flow"],
            "profile": self.profile,
        })
        return ctx


class ForecastView(ProfileRequiredMixin, TemplateView):
    """Screen 2 — the 7-day Timeline Matrix."""

    template_name = "horoscope/forecast.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        start = _today_for(self.profile)
        series = snapshot.flow_series(self.profile, start, days=7)
        ctx["series"] = series
        ctx["svg"] = _build_trend_svg(series)
        ctx["house_labels"] = HOUSE_LABELS
        return ctx


class BlueprintView(ProfileRequiredMixin, TemplateView):
    """Screen 3 — the natal Blueprint."""

    template_name = "horoscope/blueprint.html"

    # Conventional display order for the placements table.
    PLANET_ORDER = ["sun", "moon", "mercury", "venus", "mars",
                    "jupiter", "saturn", "uranus", "neptune", "pluto"]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        chart = self.profile.natal_chart
        rows = []
        for name in self.PLANET_ORDER:
            p = chart["planets"][name]
            rows.append({
                "name": name.title(),
                "sign": p["sign"],
                "deg": int(p["deg_in_sign"]),
                "house": p["house"],
                "house_label": HOUSE_LABELS[p["house"]],
                "retrograde": p["retrograde"],
            })
        ctx.update({
            "chart": chart,
            "ascendant": chart["ascendant"],
            "sun": chart["planets"]["sun"],
            "chart_ruler": chart["chart_ruler"].title(),
            "rows": rows,
            "profile": self.profile,
        })
        return ctx


class MethodologyView(TemplateView):
    """Transparency disclosure: what is computed vs. interpreted."""

    template_name = "horoscope/methodology.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["house_labels"] = HOUSE_LABELS
        return ctx


class OnboardingView(FormView):
    """Collect birth data, compute the natal chart, create the session profile."""

    template_name = "horoscope/onboarding.html"
    form_class = OnboardingForm
    success_url = reverse_lazy("horoscope:dashboard")

    def get(self, request, *args, **kwargs):
        # If a profile already exists for this session, skip onboarding.
        key = request.session.session_key
        if key and Profile.objects.filter(session_key=key).exists():
            return redirect("horoscope:dashboard")
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        data = form.cleaned_data
        if self.request.session.session_key is None:
            self.request.session.save()  # force a session key for new visitors
        key = self.request.session.session_key

        chart = compute_natal_chart(
            data["birth_date"], data["birth_time"], data["timezone"],
            data["latitude"], data["longitude"], data["house_system"])

        Profile.objects.update_or_create(
            session_key=key,
            defaults={
                "birth_date": data["birth_date"],
                "birth_time": data["birth_time"],
                "birth_city": data["city"],
                "latitude": data["latitude"],
                "longitude": data["longitude"],
                "timezone": data["timezone"],
                "house_system": data["house_system"],
                "natal_chart": chart,
            },
        )
        return super().form_valid(form)


# --- JSON endpoints ---------------------------------------------------------

class TickerJsonView(ProfileRequiredMixin, View):
    """Live countdown data for the dashboard ticker."""

    def get(self, request, *args, **kwargs):
        today = _today_for(self.profile)
        snap = snapshot.get_or_create_snapshot(self.profile, today)
        shift = snap.payload.get("next_shift")
        if not shift:
            return JsonResponse({"label": None, "seconds_remaining": None})
        # Recompute remaining seconds against the real clock (payload is cached).
        at = datetime.fromisoformat(shift["at_utc"])
        remaining = int((at - datetime.now(ZoneInfo("UTC"))).total_seconds())
        return JsonResponse({
            "label": shift["label"],
            "at_utc": shift["at_utc"],
            "seconds_remaining": max(0, remaining),
        })


class DayDetailJsonView(ProfileRequiredMixin, View):
    """Data-drawer payload for a forecast day (today .. today+6)."""

    def get(self, request, date: str, *args, **kwargs):
        try:
            target = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            raise Http404("Bad date")
        today = _today_for(self.profile)
        if not (today <= target <= today + timedelta(days=6)):
            raise Http404("Date out of range")
        payload = snapshot.build_payload(self.profile, target)
        return JsonResponse({
            "date": target.isoformat(),
            "flow": payload["flow"],
            "scores": payload["scores"],
            "aspects": payload["aspects"][:6],
            "transits": payload["transits"],
        })


class CitySearchJsonView(View):
    """Autocomplete endpoint for the onboarding city field."""

    def get(self, request, *args, **kwargs):
        q = request.GET.get("q", "")
        return JsonResponse({"results": cities.search(q)})


# --- PWA assets -------------------------------------------------------------

class ManifestView(TemplateView):
    template_name = "horoscope/manifest.webmanifest"
    content_type = "application/manifest+json"


class ServiceWorkerView(TemplateView):
    template_name = "horoscope/sw.js"
    content_type = "application/javascript"


class OfflineView(TemplateView):
    template_name = "horoscope/offline.html"


# --- Forecast SVG helper ----------------------------------------------------

def _build_trend_svg(series: list, width: int = 320, height: int = 140) -> dict:
    """Build a smooth Catmull-Rom trend path + point coords for the forecast.

    Returns a dict the template renders into an inline SVG (server-rendered so
    it works offline with no chart library).
    """
    n = len(series)
    if n == 0:
        return {"path": "", "points": [], "width": width, "height": height}

    pad_x, pad_top, pad_bottom = 24, 16, 28
    usable_w = width - 2 * pad_x
    usable_h = height - pad_top - pad_bottom

    pts = []
    for i, day in enumerate(series):
        x = pad_x + (usable_w * i / (n - 1) if n > 1 else 0)
        y = pad_top + usable_h * (1 - day["flow"] / 100.0)
        pts.append((x, y, day))

    # Catmull-Rom -> cubic Bezier for a smooth single line.
    def coord(p):
        return p[0], p[1]

    d = f"M {pts[0][0]:.1f} {pts[0][1]:.1f}"
    for i in range(n - 1):
        p0 = coord(pts[i - 1]) if i > 0 else coord(pts[i])
        p1 = coord(pts[i])
        p2 = coord(pts[i + 1])
        p3 = coord(pts[i + 2]) if i + 2 < n else coord(pts[i + 1])
        c1x = p1[0] + (p2[0] - p0[0]) / 6
        c1y = p1[1] + (p2[1] - p0[1]) / 6
        c2x = p2[0] - (p3[0] - p1[0]) / 6
        c2y = p2[1] - (p3[1] - p1[1]) / 6
        d += f" C {c1x:.1f} {c1y:.1f} {c2x:.1f} {c2y:.1f} {p2[0]:.1f} {p2[1]:.1f}"

    points = [{
        "x": round(x, 1), "y": round(y, 1),
        "date": day["date"], "weekday": day["weekday"],
        "flow": day["flow"], "band": day["band"],
    } for (x, y, day) in pts]
    return {"path": d, "points": points, "width": width, "height": height,
            "baseline": pad_top + usable_h}
