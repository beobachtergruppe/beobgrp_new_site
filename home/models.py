from django.db.models import TextChoices
from django.db.models.fields import DateTimeField, CharField, BooleanField
from django.db.models.fields.files import ImageField
from wagtail.admin.panels.field_panel import FieldPanel
from wagtail.blocks.field_block import RichTextBlock, CharBlock
from wagtail.fields import StreamField, RichTextField
from wagtail.images.blocks import ImageChooserBlock

from wagtail.models import Page


class HomePage(Page):
    body = StreamField([
        ('heading', CharBlock(form_classname='title', label='Titel')),
        ('subheading', CharBlock(form_classname='sub-title', label='Subtitel')),
        ('paragraph', RichTextBlock()),
        ('image', ImageChooserBlock())
    ], default=[])

    content_panels = Page.content_panels + [
        FieldPanel('body')
    ]

class EventTypes(TextChoices):
    TALK = "Vortrag"
    HYBRID = "Hybride Vortrag"
    ONLINE = "Online Vortrag"
    OBSERVE = "Beobachtungsabend"
    EXCURSION = "Ausflug"


class SingleEvent(Page):
    start_time = DateTimeField()
    event_type = CharField(choices=EventTypes)
    location = CharField(blank=True, max_length=120, default="Deutsches Museum")
    referent = CharField(blank=True, max_length=120)
    abstract = RichTextField(blank=True, max_length=800)
    image = ImageField(blank=True)
    cancelled = BooleanField(default=False)

    content_panels = Page.content_panels + [
        FieldPanel('start_time'),
        FieldPanel('event_type'),
        FieldPanel('title'),
        FieldPanel('location'),
        FieldPanel('referent'),
        FieldPanel('abstract'),
        FieldPanel('image'),
        FieldPanel('cancelled')
    ]

class EventPage(HomePage):
    child_page_types = [SingleEvent]
