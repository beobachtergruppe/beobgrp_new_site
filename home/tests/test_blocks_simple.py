"""
Simplified tests for common blocks
"""
from django.test import TestCase

from home.models.common import LinkBlock, ImageWithCaptionBlock


class LinkBlockSimpleTests(TestCase):
    """Basic tests for LinkBlock."""

    def test_link_block_has_correct_fields(self):
        """Test that LinkBlock has the expected field structure."""
        block = LinkBlock()
        
        # Verify the block exists and has the expected fields
        self.assertTrue(hasattr(block, 'child_blocks'))
        self.assertIn('link_type', block.child_blocks)
        self.assertIn('internal_page', block.child_blocks)
        self.assertIn('external_url', block.child_blocks)


class ImageWithCaptionBlockSimpleTests(TestCase):
    """Basic tests for ImageWithCaptionBlock."""
    
    def test_image_block_exists(self):
        """Test that ImageWithCaptionBlock can be instantiated."""
        block = ImageWithCaptionBlock()
        self.assertTrue(hasattr(block, 'child_blocks'))
        
    def test_image_block_has_required_fields(self):
        """Test that ImageWithCaptionBlock has image and caption fields."""
        block = ImageWithCaptionBlock()
        self.assertIn('image', block.child_blocks)
        self.assertIn('caption', block.child_blocks)
