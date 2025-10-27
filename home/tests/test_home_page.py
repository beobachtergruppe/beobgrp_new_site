"""
Simple tests for HomePage model
"""
from django.test import TestCase
from wagtail.models import Page
from wagtail.rich_text import RichText

from home.models import HomePage


class HomePageSimpleTests(TestCase):
    """Simple tests for HomePage model"""

    def test_homepage_can_be_instantiated(self):
        """Test that HomePage can be instantiated"""
        home_page = HomePage(title="Test", slug="test")
        self.assertEqual(home_page.title, "Test")

    def test_homepage_subpage_types_defined(self):
        """Test that HomePage has subpage types defined"""
        self.assertIsNotNone(HomePage.subpage_types)
        self.assertIn("home.EventPage", HomePage.subpage_types)

    def test_homepage_has_body_field(self):
        """Test that HomePage has a body field"""
        home_page = HomePage(title="Test", slug="test")
        self.assertTrue(hasattr(home_page, 'body'))

    def test_homepage_body_can_accept_content(self):
        """Test that HomePage body can accept StreamField content"""
        home_page = HomePage(title="Test", slug="test")
        home_page.body = [
            ("h1", "Welcome"),
            ("paragraph", RichText("<p>Test content</p>")),
        ]
        # Should not raise an error
        self.assertEqual(len(home_page.body), 2)
