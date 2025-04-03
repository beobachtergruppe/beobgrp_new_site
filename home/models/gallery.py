from django.db.models.fields import DateField, CharField, TimeField
from wagtail.models import Page
from django.db.models.fields.files import ImageField
from wagtail.admin.panels.field_panel import FieldPanel
from wagtail.fields import RichTextField


class PhotoPage(Page):
    photo = ImageField()
    description = RichTextField(max_length=800)
    author = CharField(max_length=120)
    date = DateField()
    time = TimeField(default=None)
    location = CharField(max_length=255)

    content_panels = Page.content_panels + [
        FieldPanel("photo",heading="Foto"),
        FieldPanel("description",heading="Beschreibung"),
        FieldPanel("author",heading="Autor"),
        FieldPanel("date",heading="Datum"),
        FieldPanel("time",heading="Uhrzeit",default=None),
        FieldPanel("location",heading="Ort")
    ]

class GalleryPage(Page):
    description = RichTextField(max_length=800,default="")
    cover_image = ImageField()

    content_panels = Page.content_panels + [
        FieldPanel("description",heading="Beschreibung"),
        FieldPanel("cover_image",heading="Titelbild")
    ]

    subpage_types = [PhotoPage]