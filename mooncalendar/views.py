from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from django.views import generic
from django.utils import timezone

from .models import CalendarEvent

class IndexView(generic.ListView):
    template_name = "mooncalendar/index.html"
    context_object_name = "latest_calendar_event_list"

    def get_queryset(self):
        """Return the last five published calendar events."""
        return CalendarEvent.objects.order_by("-id")[:5]
    
class CalendarEventListView(generic.ListView):
    model = CalendarEvent
    paginate_by = 10

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)

class CalendarEventCreateView(generic.CreateView):
    model = CalendarEvent
    fields = ["title"]

class CalendarEventDetailView(generic.DetailView):
    model = CalendarEvent
    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)

class CalendarEventUpdateView(generic.UpdateView):
    model = CalendarEvent
    fields = ["title"]
    template_name_suffix = "_update_form"
