from django.urls import path

from . import views

app_name = "horoscope"

urlpatterns = [
    path("", views.DashboardView.as_view(), name="dashboard"),
    path("forecast/", views.ForecastView.as_view(), name="forecast"),
    path("blueprint/", views.BlueprintView.as_view(), name="blueprint"),
    path("methodology/", views.MethodologyView.as_view(), name="methodology"),
    path("onboarding/", views.OnboardingView.as_view(), name="onboarding"),
    path("api/ticker/", views.TickerJsonView.as_view(), name="api-ticker"),
    path("api/day/<str:date>/", views.DayDetailJsonView.as_view(), name="api-day"),
    path("api/cities/", views.CitySearchJsonView.as_view(), name="api-cities"),
    path("manifest.webmanifest", views.ManifestView.as_view(), name="manifest"),
    path("sw.js", views.ServiceWorkerView.as_view(), name="service-worker"),
    path("offline/", views.OfflineView.as_view(), name="offline"),
]
