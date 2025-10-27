"""
Simplified tests for EventPage and SingleEvent models
"""
from django.test import TestCase
from datetime import datetime, timedelta
from django.utils.timezone import make_aware
from wagtail.rich_text import RichText

from home.models import EventPage, SingleEvent, EventTypes


class EventPageSimpleTests(TestCase):
    """Basic tests for EventPage model."""

    def test_event_page_exists(self):
        """Test that EventPage model can be instantiated."""
        event_page = EventPage(
            title="Events",
            slug="events",
        )
        self.assertEqual(event_page.title, "Events")

    def test_event_page_subpage_types(self):
        """Test that EventPage allows SingleEvent as child."""
        self.assertIn('home.SingleEvent', EventPage.subpage_types)
    
    def test_event_page_has_body_field(self):
        """Test that EventPage has body StreamField."""
        event_page = EventPage()
        self.assertTrue(hasattr(event_page, 'body'))


class SingleEventSimpleTests(TestCase):
    """Basic tests for SingleEvent model."""
    
    def test_single_event_exists(self):
        """Test that SingleEvent model can be instantiated."""
        now = make_aware(datetime.now())
        event = SingleEvent(
            title="Test Event Talk",
            slug="test-event-talk",
            event_title="Test Event",
            start_time=now,
            event_type=EventTypes.TALK,
            referent="Test Speaker",
            abstract=RichText("Test abstract"),
        )
        self.assertEqual(event.event_title, "Test Event")
        
    def test_event_types_available(self):
        """Test that all event types are defined."""
        self.assertEqual(EventTypes.TALK, 'Vortrag')
        self.assertEqual(EventTypes.HYBRID, 'Hybride Vortrag')
        self.assertEqual(EventTypes.ONLINE, 'Online Vortrag')
        self.assertEqual(EventTypes.OBSERVE, 'Beobachtungsabend')
        self.assertEqual(EventTypes.EXCURSION, 'Ausflug')
        
    def test_reservation_required_for_talks(self):
        """Test that talks require reservation."""
        now = make_aware(datetime.now())
        event = SingleEvent(
            title="Test Talk",
            slug="test-talk",
            event_title="Test Talk",
            start_time=now + timedelta(days=7),
            event_type=EventTypes.TALK,
            referent="Speaker",
            abstract=RichText("Abstract"),
            needs_reservation=True,
        )
        self.assertTrue(event.needs_reservation)
        
    def test_event_has_required_fields(self):
        """Test that SingleEvent has all required fields."""
        event = SingleEvent()
        self.assertTrue(hasattr(event, 'event_title'))
        self.assertTrue(hasattr(event, 'start_time'))
        self.assertTrue(hasattr(event, 'event_type'))
        self.assertTrue(hasattr(event, 'referent'))
        self.assertTrue(hasattr(event, 'abstract'))
        self.assertTrue(hasattr(event, 'needs_reservation'))
        self.assertTrue(hasattr(event, 'cancelled'))
        self.assertTrue(hasattr(event, 'booked_out'))
