from django.urls import path

from . import views

app_name="mooncalendar"
urlpatterns = [
    path("", views.index, name="index"),
    path("events/", views.CalendarEventListView.as_view(), name="calendarevent-list"),
    path("new-event/", views.CalendarEventCreateView.as_view(), name="calendarevent-create"),
    path("<slug:pk>/", views.CalendarEventDetailView.as_view(), name="calendarevent-detail"),
    path("<slug:pk>/update", views.CalendarEventUpdateView.as_view(), name="calendarevent-update"),
]