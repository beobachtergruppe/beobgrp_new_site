from django.db import models
from django.db.models.fields import DateField, CharField, TimeField
from wagtail.models import Page
from wagtail.admin.panels.field_panel import FieldPanel
from wagtail.fields import RichTextField

from home.models.common import CommonContextMixin, SidebarPromotionMixin
from home.models.media import MediaMixin


class PhotoPage(MediaMixin, CommonContextMixin, Page):
    """
    A gallery page for displaying photos, animated GIFs, or videos.
    Supports flexible media types while maintaining backward compatibility.
    """
    
    # Keep the old ForeignKey for backward compatibility with Wagtail Image library
    photo: models.ForeignKey = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Wagtail-Bild (veraltetes Feld - verwenden Sie stattdessen die neuen Media-Felder)",
    )
    
    description: RichTextField = RichTextField(max_length=800, default="", blank=True)
    author: CharField = CharField(max_length=120, default="", blank=True)
    date: DateField = DateField()
    time: TimeField = TimeField(blank=True, null=True)
    location: CharField = CharField(max_length=255, default="", blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("photo", heading="Foto (Alt)"),
        FieldPanel("image", heading="Bild oder animiertes GIF"),
        FieldPanel("video", heading="Videodatei"),
        FieldPanel("media_type", heading="Medientyp"),
        FieldPanel("media_alt_text", heading="Alt-Text für Barrierefreiheit"),
        FieldPanel("description", heading="Beschreibung"),
        FieldPanel("author", heading="Autor"),
        FieldPanel("date", heading="Datum"),
        FieldPanel("time", heading="Uhrzeit"),
        FieldPanel("location", heading="Ort"),
    ]

    def get_context(self, request):
        context = super().get_context(request)
        siblings: list[PhotoPage] = list(
            PhotoPage.objects.child_of(self.get_parent()).live().order_by("-date")
        )
        self_index = siblings.index(self)
        if len(siblings) > 1:
            context["previous"] = (
                siblings[self_index - 1] if self_index > 0 else siblings[-1]
            )
            context["next"] = (
                siblings[self_index + 1]
                if self_index < len(siblings) - 1
                else siblings[0]
            )
        else:
            context["previous"] = None
            context["next"] = None
        return context


class GalleryPage(CommonContextMixin, SidebarPromotionMixin, Page):
    description: RichTextField = RichTextField(max_length=800, default="")
    
    # Keep old cover_image for backward compatibility
    cover_image: models.ForeignKey = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Altes Feld - verwenden Sie stattdessen Titelmedium",
    )
    
    # New media fields for title
    cover_image_file = models.ImageField(
        upload_to="gallery_covers/%Y/%m/",
        null=True,
        blank=True,
        help_text="Bild oder GIF für die Galerie-Überschrift",
    )
    
    cover_video = models.FileField(
        upload_to="gallery_cover_videos/%Y/%m/",
        null=True,
        blank=True,
        help_text="Video für die Galerie-Überschrift",
    )
    
    MEDIA_TYPE_CHOICES = [
        ('image', 'Bild'),
        ('gif', 'Animiertes GIF'),
        ('video', 'Video'),
    ]
    
    cover_media_type = models.CharField(
        max_length=10,
        choices=MEDIA_TYPE_CHOICES,
        default='image',
        help_text="Typ des Titelmediuns",
    )

    content_panels = Page.content_panels + [
        FieldPanel("description", heading="Beschreibung"),
        FieldPanel("cover_image", heading="Titelbild (Alt)"),
        FieldPanel("cover_image_file", heading="Titelmedium (Bild/GIF)"),
        FieldPanel("cover_video", heading="Titel-Video"),
        FieldPanel("cover_media_type", heading="Typ des Titelmediuns"),
    ]

    promote_panels = SidebarPromotionMixin.promote_panels

    subpage_types = [PhotoPage]

    def get_cover_media_url(self):
        """Get the URL of the cover media file."""
        if self.cover_media_type == 'video' and self.cover_video:
            return self.cover_video.url
        elif self.cover_media_type in ('image', 'gif') and self.cover_image_file:
            return self.cover_image_file.url
        # Fallback to old cover_image
        elif self.cover_image:
            return self.cover_image.get_rendition('original').url
        return None
    
    def get_cover_media_type(self):
        """Get the type of cover media."""
        return self.cover_media_type

    def get_context(self, request):
        context = super().get_context(request)
        context["photos"] = PhotoPage.objects.child_of(self).live().order_by("-date")
        return context


class GalleryIndexPage(CommonContextMixin, SidebarPromotionMixin, Page):
    description = RichTextField(max_length=800, default="")

    content_panels = Page.content_panels + [
        FieldPanel("description", heading="Beschreibung"),
    ]

    promote_panels = SidebarPromotionMixin.promote_panels

    subpage_types = [GalleryPage]

    def get_context(self, request):
        context = super().get_context(request)
        context["galleries"] = GalleryPage.objects.child_of(self).live()
        return context
