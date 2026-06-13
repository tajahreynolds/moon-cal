from django.db import models


class Profile(models.Model):
    """A single user's birth data and computed natal chart.

    There is no login: a profile is keyed by the Django session cookie, so one
    browser session maps to one profile. ``natal_chart`` is computed once at
    onboarding (see ``services.natal.compute_natal_chart``) and cached as JSON.
    """

    HOUSE_SYSTEMS = [("W", "Whole sign"), ("P", "Placidus")]

    session_key = models.CharField(max_length=40, unique=True, db_index=True)
    birth_date = models.DateField()
    birth_time = models.TimeField()
    birth_city = models.CharField(max_length=128)  # display label, e.g. "Lisbon, PT"
    latitude = models.FloatField()
    longitude = models.FloatField()
    timezone = models.CharField(max_length=64)  # IANA name, e.g. "Europe/Lisbon"
    house_system = models.CharField(max_length=1, choices=HOUSE_SYSTEMS, default="W")
    natal_chart = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Profile {self.pk} ({self.birth_city})"


class DailySnapshot(models.Model):
    """Cached daily reading for a profile on a given local date.

    The expensive transit/aspect/scoring work runs once per profile per day
    (see ``services.snapshot.get_or_create_snapshot``); the result lives in
    ``payload`` so dashboard loads are instant.
    """

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE,
                                related_name="snapshots")
    date = models.DateField()  # profile-local date
    payload = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["profile", "date"],
                                    name="one_snapshot_per_profile_day")
        ]

    def __str__(self):
        return f"Snapshot {self.profile_id} @ {self.date}"
