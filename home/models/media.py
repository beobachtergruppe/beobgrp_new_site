"""
Media handling models and utilities for images, GIFs, and videos.
"""

from django.db import models
from django.core.files.uploadedfile import UploadedFile
from typing import Optional


class MediaMixin(models.Model):
    """
    Abstract base class for models that need to handle various media types.
    Provides flexible media handling for images, animated GIFs, and videos.
    """
    
    # Image field - supports static images and GIFs
    image = models.ImageField(
        upload_to="images/%Y/%m/",
        null=True,
        blank=True,
        help_text="Bilder als statische Dateien oder animierte GIFs (PNG, JPG, GIF)",
    )
    
    # Video field - supports common video formats
    video = models.FileField(
        upload_to="videos/%Y/%m/",
        null=True,
        blank=True,
        validators=[],  # You may add custom validators here
        help_text="Videodatei (MP4, WebM, Ogg)",
    )
    
    # Media type indicator
    MEDIA_TYPE_CHOICES = [
        ('image', 'Statisches Bild'),
        ('gif', 'Animiertes GIF'),
        ('video', 'Videodatei'),
    ]
    
    media_type = models.CharField(
        max_length=10,
        choices=MEDIA_TYPE_CHOICES,
        default='image',
        help_text="Typ des Mediums",
    )
    
    # Alternative text (used for images and videos for accessibility)
    media_alt_text = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="Beschreibung für Barrierefreiheit",
    )
    
    class Meta:
        abstract = True
    
    def get_media_file(self):
        """Get the appropriate media file based on media_type."""
        if self.media_type == 'video' and self.video:
            return self.video
        elif self.media_type in ('image', 'gif') and self.image:
            return self.image
        return None
    
    def get_media_url(self):
        """Get the URL of the current media file."""
        media_file = self.get_media_file()
        return media_file.url if media_file else None
    
    def is_gif(self) -> bool:
        """Check if the current media is an animated GIF."""
        if self.media_type == 'gif' and self.image:
            return self.image.name.lower().endswith('.gif')
        return False
    
    def is_video(self) -> bool:
        """Check if the current media is a video."""
        return self.media_type == 'video' and bool(self.video)
    
    def is_static_image(self) -> bool:
        """Check if the current media is a static image."""
        return self.media_type == 'image' and bool(self.image) and not self.is_gif()


class MediaChoiceField(models.Model):
    """
    A model to store media choice information for use in streamfield blocks.
    This provides flexibility for choosing between images, GIFs, and videos.
    """
    
    MEDIA_SOURCE_CHOICES = [
        ('wagtail_image', 'Bild aus Wagtail-Bibliothek'),
        ('gif_upload', 'Animiertes GIF hochladen'),
        ('video_upload', 'Video hochladen'),
    ]
    
    media_source = models.CharField(
        max_length=20,
        choices=MEDIA_SOURCE_CHOICES,
        default='wagtail_image',
    )
    
    class Meta:
        abstract = True
