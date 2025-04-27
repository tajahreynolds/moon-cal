from django.db import models
from django.urls import reverse

class CalendarEvent(models.Model):
    title = models.CharField(max_length=128)
    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("mooncalendar:calendarevent-detail", kwargs={"pk": self.pk})
