from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from django.views import generic

from .models import CalendarEvent

def index(request):
    return render(request, "mooncalendar/index.html")
    
class CalendarEventListView(generic.ListView):
    model = CalendarEvent
    paginate_by = 10

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        return super().get_queryset().order_by('-id')

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
