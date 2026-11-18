"""
Simplified tests for common blocks
"""

from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from wagtail.models import Page

from home.models import EventPage, HomePage
from home.models.common import (
    BlogListBlock,
    ImageWithCaptionBlock,
    LinkBlock,
    VideoWithCaptionBlock,
)


class LinkBlockSimpleTests(TestCase):
    """Basic tests for LinkBlock."""

    def test_link_block_has_correct_fields(self):
        """Test that LinkBlock has the expected field structure."""
        block = LinkBlock()

        # Verify the block exists and has the expected fields
        self.assertTrue(hasattr(block, "child_blocks"))
        self.assertIn("link_type", block.child_blocks)
        self.assertIn("internal_page", block.child_blocks)
        self.assertIn("external_url", block.child_blocks)


class ImageWithCaptionBlockSimpleTests(TestCase):
    """Basic tests for ImageWithCaptionBlock."""

    def test_image_block_exists(self):
        """Test that ImageWithCaptionBlock can be instantiated."""
        block = ImageWithCaptionBlock()
        self.assertTrue(hasattr(block, "child_blocks"))

    def test_image_block_has_required_fields(self):
        """Test that ImageWithCaptionBlock has image and caption fields."""
        block = ImageWithCaptionBlock()
        self.assertIn("image", block.child_blocks)
        self.assertIn("caption", block.child_blocks)

    def test_relative_size_choices_default_to_full_size(self):
        """Image and video caption blocks expose the same relative size options."""
        for block_class in (ImageWithCaptionBlock, VideoWithCaptionBlock):
            with self.subTest(block=block_class.__name__):
                relative_size = block_class().child_blocks["relative_size"]
                self.assertEqual(relative_size.get_default(), "1")
                self.assertEqual(
                    [value for value, _label in relative_size.field.choices],
                    ["1", "1/2", "1/4"],
                )


class BlogListBlockTests(TestCase):
    def test_is_available_in_homepage_and_multi_column_streams(self):
        body_block = HomePage._meta.get_field("body").stream_block
        multi_column = body_block.child_blocks["multi_column"]

        self.assertIn("blog_list", body_block.child_blocks)
        self.assertIn("blog_list", multi_column.child_blocks["content"].child_blocks)

    def test_excerpt_length_is_limited_to_200_characters(self):
        excerpt_length = BlogListBlock().child_blocks["excerpt_length"]

        self.assertEqual(excerpt_length.get_default(), 200)
        self.assertEqual(excerpt_length.field.max_value, 200)

    def test_lists_newest_homepage_children_with_truncated_text(self):
        root_page = Page.get_first_root_node()
        parent_page = root_page.add_child(
            instance=HomePage(title="Parent", slug="parent")
        )
        now = timezone.now()

        older_page = HomePage(
            title="Older",
            slug="older",
            body=[("paragraph", "<p>Older story</p>")],
        )
        parent_page.add_child(instance=older_page)
        older_page.live = True
        older_page.first_published_at = now - timedelta(days=2)
        older_page.save()

        newer_page = HomePage(
            title="Newer",
            slug="newer",
            body=[("paragraph", "<p>Newer story content</p>")],
        )
        parent_page.add_child(instance=newer_page)
        newer_page.live = True
        newer_page.first_published_at = now - timedelta(days=1)
        newer_page.save()

        event_page = EventPage(title="Event", slug="event")
        parent_page.add_child(instance=event_page)
        event_page.live = True
        event_page.first_published_at = now
        event_page.save()

        context = BlogListBlock().get_context(
            {"excerpt_length": 5}, {"page": parent_page}
        )

        entries = context["blog_entries"]
        self.assertEqual([entry["page"].title for entry in entries], ["Newer", "Older"])
        self.assertEqual(entries[0]["excerpt"], "Newer...")
        self.assertTrue(entries[0]["is_truncated"])
