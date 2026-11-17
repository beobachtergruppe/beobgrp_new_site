"""
Simplified tests for common blocks
"""

from django.test import TestCase

from home.models.common import (
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
