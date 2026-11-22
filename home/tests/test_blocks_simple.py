"""
Simplified tests for common blocks
"""

from datetime import timedelta
from types import SimpleNamespace

from django.template import Context, Template
from django.test import TestCase
from django.utils import timezone
from wagtail.models import Page

from home.models import EventPage, HomePage
from home.models.events import SingleEvent
from home.models.gallery import GalleryIndexPage, GalleryPage, PhotoPage, VideoPage
from home.models.common import (
    BlogListBlock,
    ImageWithCaptionBlock,
    LinkBlock,
    VideoWithCaptionBlock,
    _page_preview_image,
    _page_preview_text,
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
    def test_caption_only_pages_use_image_and_video_captions_as_preview_text(self):
        captions = (
            ("image_with_caption", "An image caption"),
            ("video_with_caption", "A video caption"),
        )

        for block_type, caption in captions:
            with self.subTest(block_type=block_type):
                page = SimpleNamespace(
                    body=[
                        SimpleNamespace(
                            block_type=block_type,
                            value={"caption": f"<p>{caption}</p>"},
                        )
                    ]
                )

                self.assertEqual(_page_preview_text(page), caption)

    def test_sidebar_icon_is_used_for_video_only_blog_preview(self):
        sidebar_icon = object()
        page = SimpleNamespace(
            body=[
                SimpleNamespace(
                    block_type="video_with_caption",
                    value={"media_file": object()},
                )
            ],
            sidebar_icon=sidebar_icon,
        )

        self.assertIs(_page_preview_image(page), sidebar_icon)

    def test_only_homepage_exposes_publication_date_in_promote_tab(self):
        self.assertIsNotNone(HomePage._meta.get_field("publication_date"))
        self.assertIn(
            "publication_date",
            {getattr(panel, "field_name", None) for panel in HomePage.promote_panels},
        )

        other_page_models = (
            EventPage,
            GalleryIndexPage,
            GalleryPage,
            PhotoPage,
            VideoPage,
            SingleEvent,
        )

        for page_model in other_page_models:
            with self.subTest(page_model=page_model.__name__):
                self.assertNotIn(
                    "publication_date",
                    {field.name for field in page_model._meta.get_fields()},
                )

    def test_is_available_in_homepage_and_multi_column_streams(self):
        body_block = HomePage._meta.get_field("body").stream_block
        multi_column = body_block.child_blocks["multi_column"]

        self.assertIn("blog_list", body_block.child_blocks)
        self.assertIn("blog_list", multi_column.child_blocks["content"].child_blocks)

    def test_blog_list_renders_when_nested_in_multi_column(self):
        root_page = Page.get_first_root_node()
        parent_page = root_page.add_child(
            instance=HomePage(
                title="Parent",
                slug="parent",
                body=[
                    (
                        "multi_column",
                        {
                            "max_columns": "1",
                            "min_columns": "1",
                            "width": "full",
                            "content": [
                                ("blog_list", {"excerpt_length": 200}),
                            ],
                        },
                    ),
                ],
            )
        )
        child_page = HomePage(
            title="Nested story",
            slug="nested-story",
            body=[("paragraph", "<p>A nested excerpt</p>")],
        )
        parent_page.add_child(instance=child_page)
        child_page.live = True
        child_page.save()

        rendered = Template("{% load wagtailcore_tags %}{% include_block page.body %}").render(
            Context({"page": parent_page})
        )

        self.assertIn("Nested story", rendered)
        self.assertIn("A nested excerpt", rendered)
        self.assertIn("Weiterlesen", rendered)

    def test_excerpt_length_is_limited_to_200_characters(self):
        excerpt_length = BlogListBlock().child_blocks["excerpt_length"]

        self.assertEqual(excerpt_length.get_default(), 200)
        self.assertEqual(excerpt_length.field.max_value, 200)
        self.assertNotIn("sort_by_publication_date", BlogListBlock().child_blocks)

    def test_lists_children_by_publication_date_with_fallback_and_truncated_text(self):
        root_page = Page.get_first_root_node()
        parent_page = root_page.add_child(instance=HomePage(title="Parent", slug="parent"))
        now = timezone.now()

        older_page = HomePage(
            title="Older",
            slug="older",
            body=[("paragraph", "<p>Older story</p>")],
            publication_date=now.date(),
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
            {"excerpt_length": 5},
            {"page": parent_page},
        )

        entries = context["blog_entries"]
        self.assertEqual([entry["page"].title for entry in entries], ["Older", "Newer"])
        self.assertEqual(entries[0]["excerpt"], "Older...")
        self.assertTrue(entries[0]["is_truncated"])
