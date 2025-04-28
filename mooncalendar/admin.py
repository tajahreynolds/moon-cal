from django.contrib import admin

from .models import CalendarEvent

class CalendarEventAdmin(admin.ModelAdmin):
    fields = ["title"]

admin.site.register(CalendarEvent, CalendarEventAdmin)