"""
Simplified tests for Gallery models
"""
from django.test import TestCase
from wagtail.rich_text import RichText

from home.models import GalleryIndexPage, GalleryPage, PhotoPage


class GallerySimpleTests(TestCase):
    """Basic tests for Gallery models."""

    def test_gallery_index_exists(self):
        """Test that GalleryIndexPage model can be instantiated."""
        gallery_index = GalleryIndexPage(
            title="Gallery",
            slug="gallery",
        )
        self.assertEqual(gallery_index.title, "Gallery")

    def test_gallery_index_subpage_types(self):
        """Test that GalleryIndexPage can have GalleryPage as child."""
        # subpage_types is a list of classes, not strings
        self.assertEqual(len(GalleryIndexPage.subpage_types), 1)
        self.assertEqual(GalleryIndexPage.subpage_types[0].__name__, 'GalleryPage')
    
    def test_gallery_page_exists(self):
        """Test that GalleryPage model can be instantiated."""
        gallery = GalleryPage(
            title="Test Gallery",
            slug="test-gallery",
            description=RichText("Test description"),
        )
        self.assertEqual(gallery.title, "Test Gallery")
        
    def test_gallery_page_subpage_types(self):
        """Test that GalleryPage can have PhotoPage as child."""
        # subpage_types is a list of classes, not strings
        self.assertEqual(len(GalleryPage.subpage_types), 1)
        self.assertEqual(GalleryPage.subpage_types[0].__name__, 'PhotoPage')
        
    def test_photo_page_exists(self):
        """Test that PhotoPage model can be instantiated."""
        photo = PhotoPage(
            title="Test Photo",
            slug="test-photo",
        )
        self.assertEqual(photo.title, "Test Photo")
        
    def test_photo_page_has_required_fields(self):
        """Test that PhotoPage has all required fields."""
        photo = PhotoPage()
        self.assertTrue(hasattr(photo, 'photo'))
        self.assertTrue(hasattr(photo, 'date'))
        self.assertTrue(hasattr(photo, 'description'))
