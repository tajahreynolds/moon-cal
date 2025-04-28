from django.db import models
from django.urls import reverse
from django.db.models import Q, CheckConstraint

class CalendarEvent(models.Model):
    title = models.CharField(max_length=128, blank=False, null=False)

    class Meta:
        constraints = [
            CheckConstraint(check=~Q(title=""), name="calendar_event_title_not_empty")
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("mooncalendar:calendarevent-detail", kwargs={"pk": self.pk})
