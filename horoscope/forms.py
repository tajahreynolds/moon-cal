"""Onboarding form: birth data in, validated lat/lon/timezone out.

The visible city field drives an autocomplete against the bundled city list
(JS fills the hidden lat/lon/tz). If the city isn't found, the user can expand
a manual section and enter coordinates + timezone directly. Either path must
yield a valid IANA timezone and numeric coordinates.
"""

from __future__ import annotations

from zoneinfo import available_timezones

from django import forms

from .services import cities

_VALID_TZS = available_timezones()


class OnboardingForm(forms.Form):
    birth_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}),
        help_text="Your date of birth.",
    )
    birth_time = forms.TimeField(
        widget=forms.TimeInput(attrs={"type": "time"}),
        help_text="As exact as you can — the Ascendant and houses depend on it.",
    )
    city = forms.CharField(
        max_length=128,
        widget=forms.TextInput(attrs={"autocomplete": "off",
                                      "placeholder": "Start typing a city…"}),
        help_text="Birth city.",
    )
    house_system = forms.ChoiceField(
        choices=[("W", "Whole sign (recommended)"), ("P", "Placidus")],
        initial="W", required=False,
    )

    # Hidden fields filled by the autocomplete JS, or by the manual section.
    latitude = forms.FloatField(required=False, widget=forms.HiddenInput())
    longitude = forms.FloatField(required=False, widget=forms.HiddenInput())
    timezone = forms.CharField(required=False, max_length=64,
                               widget=forms.HiddenInput())

    def clean(self):
        cleaned = super().clean()
        lat = cleaned.get("latitude")
        lon = cleaned.get("longitude")
        tz = cleaned.get("timezone")
        city = cleaned.get("city")

        # If coordinates weren't resolved client-side, try the city list server-side.
        if (lat is None or lon is None or not tz) and city:
            match = cities.get(city.split(",")[0].strip())
            if match:
                lat, lon, tz = match["lat"], match["lon"], match["tz"]
                cleaned["latitude"], cleaned["longitude"] = lat, lon
                cleaned["timezone"] = tz
                cleaned["city"] = match["label"]

        if lat is None or lon is None or not tz:
            raise forms.ValidationError(
                "Could not resolve a location. Pick a city from the list or "
                "enter coordinates and timezone manually.")
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            raise forms.ValidationError("Coordinates are out of range.")
        if tz not in _VALID_TZS:
            raise forms.ValidationError(f"Unknown timezone: {tz!r}.")
        cleaned.setdefault("house_system", "W")
        cleaned["house_system"] = cleaned.get("house_system") or "W"
        return cleaned
