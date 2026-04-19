from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.fields import DateField, CharField, TimeField
from wagtail.models import Page
from wagtail.admin.panels.field_panel import FieldPanel
from wagtail.fields import RichTextField

from home.models.common import CommonContextMixin, SidebarPromotionMixin

ALLOWED_MEDIA_EXTENSIONS = (".gif", ".mp4", ".webm", ".ogg", ".ogv")


def validate_media_file(file):
    """Accept only GIF and common video formats; reject all other files."""
    name = file.name.lower()
    if not any(name.endswith(ext) for ext in ALLOWED_MEDIA_EXTENSIONS):
        raise ValidationError(
            f"Nur GIF- und Videodateien sind erlaubt (GIF, MP4, WebM, Ogg). "
            f"Die hochgeladene Datei '{file.name}' wird nicht unterstützt."
        )


class PhotoPage(CommonContextMixin, Page):
    """
    A gallery page for displaying static photos.
    """
    
    # Keep the old ForeignKey for backward compatibility with Wagtail Image library
    photo: models.ForeignKey = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Wagtail-Bild",
    )
    
    description: RichTextField = RichTextField(max_length=800, default="", blank=True)
    author: CharField = CharField(max_length=120, default="", blank=True)
    date: DateField = DateField()
    time: TimeField = TimeField(blank=True, null=True)
    location: CharField = CharField(max_length=255, default="", blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("photo", heading="Foto"),
        FieldPanel("description", heading="Beschreibung"),
        FieldPanel("author", heading="Autor"),
        FieldPanel("date", heading="Datum"),
        FieldPanel("time", heading="Uhrzeit"),
        FieldPanel("location", heading="Ort"),
    ]

    def _get_gallery_siblings(self):
        """Get all gallery items (PhotoPage and VideoPage) ordered by date."""
        parent = self.get_parent()
        photos = PhotoPage.objects.child_of(parent).live().order_by("-date")
        videos = VideoPage.objects.child_of(parent).live().order_by("-date")
        
        # Combine and sort by date
        all_items = sorted(
            list(photos) + list(videos),
            key=lambda x: x.date,
            reverse=True
        )
        return all_items

    def get_context(self, request):
        context = super().get_context(request)
        siblings = self._get_gallery_siblings()
        
        try:
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
        except ValueError:
            context["previous"] = None
            context["next"] = None
        
        return context


class VideoPage(CommonContextMixin, Page):
    """
    A gallery page for displaying animated GIFs and videos.
    """

    MEDIA_TYPE_CHOICES = [
        ("gif", "Animiertes GIF"),
        ("video", "Videodatei"),
    ]

    media_file = models.FileField(
        upload_to="videos/%Y/%m/",
        null=True,
        blank=True,
        help_text="Videodatei (MP4, WebM, Ogg) oder animiertes GIF",
        validators=[validate_media_file],
    )
    media_type = models.CharField(
        max_length=10,
        choices=MEDIA_TYPE_CHOICES,
        default="video",
        help_text="Typ des Mediums",
    )
    media_alt_text = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="Beschreibung für Barrierefreiheit",
    )
    description: RichTextField = RichTextField(max_length=800, default="", blank=True)
    author: CharField = CharField(max_length=120, default="", blank=True)
    date: DateField = DateField()
    time: TimeField = TimeField(blank=True, null=True)
    location: CharField = CharField(max_length=255, default="", blank=True)

    content_panels = Page.content_panels + [
        FieldPanel(
            "media_file",
            heading="Videodatei oder animiertes GIF",
            attrs={"accept": ".gif,.mp4,.webm,.ogg,.ogv,image/gif,video/mp4,video/webm,video/ogg"},
        ),
        FieldPanel("media_type", heading="Medientyp"),
        FieldPanel("media_alt_text", heading="Alt-Text für Barrierefreiheit"),
        FieldPanel("description", heading="Beschreibung"),
        FieldPanel("author", heading="Autor"),
        FieldPanel("date", heading="Datum"),
        FieldPanel("time", heading="Uhrzeit"),
        FieldPanel("location", heading="Ort"),
    ]

    def clean(self):
        super().clean()
        if self.media_file and self.media_type:
            is_gif = self.media_file.name.lower().endswith(".gif")
            if is_gif and self.media_type != "gif":
                raise ValidationError(
                    {"media_type": "Die hochgeladene Datei ist ein GIF. Bitte wähle 'Animiertes GIF' als Medientyp."}
                )
            if not is_gif and self.media_type == "gif":
                raise ValidationError(
                    {"media_type": "Die hochgeladene Datei ist kein GIF. Bitte wähle 'Videodatei' als Medientyp."}
                )

    def is_gif(self) -> bool:
        return self.media_type == "gif" and bool(self.media_file)

    def is_video(self) -> bool:
        return self.media_type == "video" and bool(self.media_file)

    def get_media_url(self):
        return self.media_file.url if self.media_file else None

    def _get_gallery_siblings(self):
        """Get all gallery items (PhotoPage and VideoPage) ordered by date."""
        parent = self.get_parent()
        photos = PhotoPage.objects.child_of(parent).live().order_by("-date")
        videos = VideoPage.objects.child_of(parent).live().order_by("-date")
        
        # Combine and sort by date
        all_items = sorted(
            list(photos) + list(videos),
            key=lambda x: x.date,
            reverse=True
        )
        return all_items

    def get_context(self, request):
        context = super().get_context(request)
        siblings = self._get_gallery_siblings()
        
        try:
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
        except ValueError:
            context["previous"] = None
            context["next"] = None
        
        return context


class GalleryPage(CommonContextMixin, SidebarPromotionMixin, Page):
    description: RichTextField = RichTextField(max_length=800, default="")
    cover_image: models.ForeignKey = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    content_panels = Page.content_panels + [
        FieldPanel("description", heading="Beschreibung"),
        FieldPanel("cover_image", heading="Titelbild"),
    ]

    promote_panels = SidebarPromotionMixin.promote_panels

    subpage_types = [PhotoPage, VideoPage]

    def get_context(self, request):
        context = super().get_context(request)
        photos = PhotoPage.objects.child_of(self).live().order_by("-date")
        videos = VideoPage.objects.child_of(self).live().order_by("-date")
        
        # Combine and sort by date
        all_items = sorted(
            list(photos) + list(videos),
            key=lambda x: x.date,
            reverse=True
        )
        context["photos"] = all_items
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
