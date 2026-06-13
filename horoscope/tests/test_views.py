"""View/integration tests: onboarding, the three screens, JSON endpoints, PWA.

These mirror the style of ``mooncalendar/tests.py`` (TestCase + reverse +
assertContains) and exercise the real ephemeris/scoring stack end to end.
"""

from datetime import date, timedelta

from django.test import TestCase
from django.urls import reverse

from horoscope.models import DailySnapshot, Profile
from horoscope.services import cities


def _onboard(client, city="New York"):
    """Complete onboarding for the test client's session."""
    match = cities.get(city)
    return client.post(reverse("horoscope:onboarding"), {
        "birth_date": "1990-07-15",
        "birth_time": "14:30",
        "city": match["label"],
        "latitude": match["lat"],
        "longitude": match["lon"],
        "timezone": match["tz"],
        "house_system": "W",
    })


class OnboardingFlowTests(TestCase):
    def test_dashboard_redirects_without_profile(self):
        response = self.client.get(reverse("horoscope:dashboard"))
        self.assertRedirects(response, reverse("horoscope:onboarding"))

    def test_onboarding_creates_profile_with_chart(self):
        response = _onboard(self.client)
        self.assertRedirects(response, reverse("horoscope:dashboard"))
        self.assertEqual(Profile.objects.count(), 1)
        profile = Profile.objects.get()
        self.assertEqual(profile.birth_city, "New York, US")
        self.assertEqual(len(profile.natal_chart["planets"]), 10)
        self.assertIn("ascendant", profile.natal_chart)

    def test_onboarding_rejects_unresolved_location(self):
        response = self.client.post(reverse("horoscope:onboarding"), {
            "birth_date": "1990-07-15", "birth_time": "14:30",
            "city": "Nowheresville", "house_system": "W",
        })
        self.assertEqual(response.status_code, 200)  # re-render with error
        self.assertEqual(Profile.objects.count(), 0)


class DashboardTests(TestCase):
    def setUp(self):
        _onboard(self.client)

    def test_dashboard_shows_three_directives(self):
        response = self.client.get(reverse("horoscope:dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ENERGY STATUS")
        self.assertContains(response, "MENTAL FOCUS")
        self.assertContains(response, "FRICTION WARN")

    def test_snapshot_is_cached(self):
        # Two dashboard loads must reuse a single DailySnapshot row.
        self.client.get(reverse("horoscope:dashboard"))
        self.client.get(reverse("horoscope:dashboard"))
        self.assertEqual(DailySnapshot.objects.count(), 1)

    def test_ticker_returns_json(self):
        response = self.client.get(reverse("horoscope:api-ticker"))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("seconds_remaining", data)
        if data["seconds_remaining"] is not None:
            self.assertGreaterEqual(data["seconds_remaining"], 0)


class ForecastTests(TestCase):
    def setUp(self):
        _onboard(self.client)

    def test_forecast_has_seven_days(self):
        response = self.client.get(reverse("horoscope:forecast"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["series"]), 7)
        self.assertEqual(response.context["svg"]["points"].__len__(), 7)

    def test_day_detail_in_range(self):
        today = date.today().isoformat()
        response = self.client.get(
            reverse("horoscope:api-day", kwargs={"date": today}))
        self.assertEqual(response.status_code, 200)
        self.assertIn("aspects", response.json())

    def test_day_detail_bad_date_404(self):
        response = self.client.get(
            reverse("horoscope:api-day", kwargs={"date": "not-a-date"}))
        self.assertEqual(response.status_code, 404)

    def test_day_detail_out_of_range_404(self):
        far = (date.today() + timedelta(days=60)).isoformat()
        response = self.client.get(
            reverse("horoscope:api-day", kwargs={"date": far}))
        self.assertEqual(response.status_code, 404)


class BlueprintTests(TestCase):
    def setUp(self):
        _onboard(self.client)

    def test_blueprint_shows_placements(self):
        response = self.client.get(reverse("horoscope:blueprint"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["rows"]), 10)
        self.assertContains(response, "Ascendant")
        self.assertContains(response, "Chart ruler")
        # Every row carries a one-word house label from HOUSE_LABELS.
        from horoscope.services.scoring import HOUSE_LABELS
        for row in response.context["rows"]:
            self.assertIn(row["house_label"], HOUSE_LABELS.values())


class CitySearchTests(TestCase):
    def test_city_search_returns_results(self):
        response = self.client.get(reverse("horoscope:api-cities"), {"q": "lond"})
        self.assertEqual(response.status_code, 200)
        labels = [r["label"] for r in response.json()["results"]]
        self.assertTrue(any("London" in lbl for lbl in labels))

    def test_empty_query_returns_nothing(self):
        response = self.client.get(reverse("horoscope:api-cities"), {"q": ""})
        self.assertEqual(response.json()["results"], [])


class PwaAssetTests(TestCase):
    def test_manifest_served_with_correct_type(self):
        response = self.client.get(reverse("horoscope:manifest"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/manifest+json")

    def test_service_worker_served(self):
        response = self.client.get(reverse("horoscope:service-worker"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("javascript", response["Content-Type"])

    def test_methodology_renders(self):
        response = self.client.get(reverse("horoscope:methodology"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "FACT")
        self.assertContains(response, "OUR READ")
