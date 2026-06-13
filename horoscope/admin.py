from django.contrib import admin

from .models import DailySnapshot, Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "birth_city", "birth_date", "house_system", "created_at")
    readonly_fields = ("natal_chart", "created_at")
    search_fields = ("birth_city", "session_key")


@admin.register(DailySnapshot)
class DailySnapshotAdmin(admin.ModelAdmin):
    list_display = ("id", "profile", "date", "created_at")
    readonly_fields = ("payload", "created_at")
    list_filter = ("date",)
