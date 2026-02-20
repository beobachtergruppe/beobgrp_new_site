from django.db import models
from django.db.models.fields import DateField, CharField, TimeField
from wagtail.models import Page
from wagtail.admin.panels.field_panel import FieldPanel
from wagtail.fields import RichTextField

from home.models.common import CommonContextMixin


class PhotoPage(CommonContextMixin, Page):
    photo: models.ForeignKey = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
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

    def get_context(self, request):
        context = super().get_context(request)
        siblings: list[PhotoPage] = list(PhotoPage.objects.child_of(self.get_parent()).live().order_by("-date"))
        self_index = siblings.index(self)
        if len(siblings) > 1:
            context["previous"] = (
                siblings[self_index - 1] if self_index > 0 else siblings[-1]
            )
            context["next"] = (
                siblings[self_index + 1] if self_index < len(siblings) - 1 else siblings[0]
            )
        else:
            context["previous"] = None
            context["next"] = None
        return context


class GalleryPage(CommonContextMixin, Page):
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

    subpage_types = [PhotoPage]

    def get_context(self, request):
        context = super().get_context(request)
        context["photos"] = PhotoPage.objects.child_of(self).live().order_by("-date")
        return context


class GalleryIndexPage(CommonContextMixin, Page):
    description = RichTextField(max_length=800, default="")

    content_panels = Page.content_panels + [
        FieldPanel("description", heading="Beschreibung"),
    ]

    subpage_types = [GalleryPage]

    def get_context(self, request):
        context = super().get_context(request)
        context["galleries"] = GalleryPage.objects.child_of(self).live()
        return context
