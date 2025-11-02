"""
Simple integration test to verify the test setup works.
This test can be run to ensure the testing infrastructure is properly configured.
"""
from django.test import TestCase
from wagtail.models import Page, Site


class TestSetupTest(TestCase):
    """Basic test to verify Django/Wagtail test setup is working"""

    def test_can_create_page(self):
        """Test that we can create a basic Page"""
        root = Page.get_first_root_node()
        self.assertIsNotNone(root)
        self.assertTrue(isinstance(root, Page))

    def test_can_create_site(self):
        """Test that we can create a Site"""
        root = Page.get_first_root_node()
        site = Site.objects.create(
            hostname="testserver",
            root_page=root,
            is_default_site=True,
            site_name="testserver",
        )
        self.assertIsNotNone(site)
        self.assertEqual(site.hostname, "testserver")

    def test_home_models_importable(self):
        """Test that all home models can be imported"""
        from home.models import (
            HomePage,
            EventPage,
            SingleEvent,
            GalleryIndexPage,
            GalleryPage,
            PhotoPage,
        )
        
        # If we get here without ImportError, the test passes
        self.assertTrue(True)
