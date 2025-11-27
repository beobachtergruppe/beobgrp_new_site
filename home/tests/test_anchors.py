"""
Tests for anchor link functionality
"""
from django.test import TestCase
from wagtail.models import Page
from wagtail.rich_text import RichText

from home.models import HomePage, EventPage
from home.models.common import generate_anchor_id


class AnchorGenerationTests(TestCase):
    """Tests for anchor ID generation"""

    def test_generate_anchor_id_basic(self):
        """Test basic anchor ID generation"""
        result = generate_anchor_id("Welcome")
        self.assertEqual(result, "block-welcome")

    def test_generate_anchor_id_with_spaces(self):
        """Test anchor ID generation with spaces"""
        result = generate_anchor_id("About Us")
        self.assertEqual(result, "block-about-us")

    def test_generate_anchor_id_with_umlauts(self):
        """Test anchor ID generation with German umlauts"""
        result = generate_anchor_id("Über Uns")
        self.assertEqual(result, "block-uber-uns")

    def test_generate_anchor_id_with_numbers(self):
        """Test anchor ID generation with numbers"""
        result = generate_anchor_id("Programm 2024")
        self.assertEqual(result, "block-programm-2024")

    def test_generate_anchor_id_with_special_chars(self):
        """Test anchor ID generation with special characters"""
        result = generate_anchor_id("FAQ & Kontakt")
        self.assertEqual(result, "block-faq-kontakt")

    def test_generate_anchor_id_with_punctuation(self):
        """Test anchor ID generation with punctuation"""
        result = generate_anchor_id("Willkommen!")
        self.assertEqual(result, "block-willkommen")

    def test_generate_anchor_id_case_insensitive(self):
        """Test that anchor IDs are lowercase"""
        result = generate_anchor_id("HELLO WORLD")
        self.assertEqual(result, "block-hello-world")

    def test_generate_anchor_id_empty_string(self):
        """Test anchor ID generation with empty string"""
        result = generate_anchor_id("")
        self.assertEqual(result, "block-")


class PageAnchorExtractionTests(TestCase):
    """Tests for extracting anchors from pages"""

    def setUp(self):
        """Set up test pages with content"""
        # Get the root page
        self.root = Page.objects.get(id=1)

    def test_homepage_has_get_anchors_method(self):
        """Test that HomePage has get_anchors method"""
        home = HomePage(
            title="Test Home",
            slug="test-home",
        )
        self.assertTrue(hasattr(home, 'get_anchors'))
        self.assertTrue(callable(home.get_anchors))

    def test_get_anchors_with_headings(self):
        """Test extracting anchors from a page with headings"""
        home = HomePage(
            title="Test Home",
            slug="test-home",
        )
        home.body = [
            ("h1", "Welcome"),
            ("h2", "About Us"),
            ("paragraph", RichText("<p>Some text</p>")),
            ("h3", "Contact"),
        ]
        
        anchors = home.get_anchors()
        
        # Should have 3 anchors (h1, h2, h3)
        self.assertEqual(len(anchors), 3)
        
        # Check anchor format: list of tuples (anchor_id, text)
        self.assertEqual(anchors[0], ("block-welcome", "Welcome"))
        self.assertEqual(anchors[1], ("block-about-us", "About Us"))
        self.assertEqual(anchors[2], ("block-contact", "Contact"))

    def test_get_anchors_without_headings(self):
        """Test extracting anchors from a page without headings"""
        home = HomePage(
            title="Test Home",
            slug="test-home",
        )
        home.body = [
            ("paragraph", RichText("<p>Just a paragraph</p>")),
            ("paragraph", RichText("<p>Another paragraph</p>")),
        ]
        
        anchors = home.get_anchors()
        
        # Should have no anchors
        self.assertEqual(len(anchors), 0)

    def test_get_anchors_empty_body(self):
        """Test extracting anchors from a page with empty body"""
        home = HomePage(
            title="Test Home",
            slug="test-home",
        )
        home.body = []
        
        anchors = home.get_anchors()
        
        # Should have no anchors
        self.assertEqual(len(anchors), 0)

    def test_get_anchors_on_event_page(self):
        """Test that EventPage also supports anchor extraction"""
        event_page = EventPage(
            title="Test Events",
            slug="test-events",
        )
        
        # EventPage should also have get_anchors method (from CommonContextMixin)
        self.assertTrue(hasattr(event_page, 'get_anchors'))
        
        event_page.body = [
            ("h1", "Upcoming Events"),
            ("h2", "Past Events"),
        ]
        
        anchors = event_page.get_anchors()
        
        self.assertEqual(len(anchors), 2)
        self.assertEqual(anchors[0], ("block-upcoming-events", "Upcoming Events"))
        self.assertEqual(anchors[1], ("block-past-events", "Past Events"))

    def test_anchors_with_duplicate_headings(self):
        """Test that duplicate headings generate identical anchor IDs"""
        home = HomePage(
            title="Test Home",
            slug="test-home",
        )
        home.body = [
            ("h1", "Welcome"),
            ("h2", "Welcome"),
        ]
        
        anchors = home.get_anchors()
        
        # Both should have the same anchor ID (slugify produces same result)
        self.assertEqual(len(anchors), 2)
        self.assertEqual(anchors[0][0], "block-welcome")
        self.assertEqual(anchors[1][0], "block-welcome")
        # This is expected behavior - browsers handle duplicate IDs by jumping to first match

    def test_anchors_preserve_heading_text(self):
        """Test that original heading text is preserved in anchor data"""
        home = HomePage(
            title="Test Home",
            slug="test-home",
        )
        original_text = "Über Uns & Kontakt!"
        home.body = [
            ("h1", original_text),
        ]
        
        anchors = home.get_anchors()
        
        # Text should be preserved as-is, only ID is slugified
        self.assertEqual(len(anchors), 1)
        self.assertEqual(anchors[0][1], original_text)
        self.assertEqual(anchors[0][0], "block-uber-uns-kontakt")
