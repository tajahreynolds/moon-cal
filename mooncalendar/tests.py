from django.test import TestCase
from django.urls import reverse

from .models import CalendarEvent

def create_calendarevent(title):
    """ Create a calendar event with the given `title`. """
    return CalendarEvent.objects.create(title=title)

class CalendarEventListViewTests(TestCase):
    def test_no_calendarevents(self):
        """ If no calendar events exist, an appropriate message is displayed. """
        response = self.client.get(reverse("mooncalendar:calendarevent-list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No calendar events yet.")
        self.assertQuerySetEqual(response.context["object_list"], [])
    
    def test_create_invalid_calendarevent(self):
        """ Calendar events without a title are not added to the database. """
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError) as context:
            create_calendarevent(title="")
        self.assertTrue("violates check constraint \"calendar_event_title_not_empty\"" in str(context.exception))
    
    def test_calendarevent(self):
        """ Calendar events with a title are displayed on the list page. """
        calendar_event = create_calendarevent(title="Test Calendar Event")
        response = self.client.get(reverse("mooncalendar:calendarevent-list"))
        self.assertQuerySetEqual(response.context["object_list"], [calendar_event])
    
    def test_calendarevent_details(self):
        """ Calendar events have an associated details page. """
        calendar_event = create_calendarevent(title="Test Calendar Event Details")
        response = self.client.get(reverse("mooncalendar:calendarevent-detail", kwargs={"pk": calendar_event.pk}))
        self.assertEqual(response.context["object"], calendar_event)

    def test_two_calendarevents(self):
        """ The calendar events list page may display multiple calendar events. """
        calendar_event_1 = create_calendarevent(title="Test Calendar Event 1")
        calendar_event_2 = create_calendarevent(title="Test Calendar Event 2")
        response = self.client.get(reverse("mooncalendar:calendarevent-list"))
        self.assertQuerySetEqual(response.context["object_list"], [calendar_event_2, calendar_event_1])


class CalendarEventTests(TestCase):
    def test_case_works(self):
        """ returns True """
        self.assertTrue(True)
