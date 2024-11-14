from django.db.models import TextChoices
from django.db.models.fields import DateTimeField, CharField, BooleanField
from django.db.models.fields.files import ImageField
from wagtail.admin.panels.field_panel import FieldPanel
from wagtail.blocks.field_block import RichTextBlock, CharBlock, ChoiceBlock
from wagtail.blocks.struct_block import StructBlock
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
        FieldPanel('body', heading='Inhalt')
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
    booked_out = BooleanField(default=False)

    content_panels = Page.content_panels + [
        FieldPanel('start_time', heading='Zeit'),
        FieldPanel('event_type', heading='Art der Veranstaltung'),
        FieldPanel('title', heading='Titel'),
        FieldPanel('location', heading='Ort'),
        FieldPanel('referent', heading='Referent'),
        FieldPanel('abstract', heading='Zusammenfassung'),
        FieldPanel('image', heading='Foto'),
        FieldPanel('cancelled', heading='Abgesagt'),
        FieldPanel('booked_out', heading='Ausgebucht')
    ]


class EventListBlock(StructBlock):
    event_type = ChoiceBlock(choices=EventTypes.choices, required=True, label="Art der Veranstaltung",
                             help_text="Liste von Veranstaltungen")

class EventPage(Page):
    body = StreamField([
        ('heading', CharBlock(form_classname='title', label='Titel')),
        ('subheading', CharBlock(form_classname='sub-title', label='Subtitel')),
        ('paragraph', RichTextBlock()),
        ('image', ImageChooserBlock()),
        ('event_list', EventListBlock())
    ], default=[])

    content_panels = Page.content_panels + [
        FieldPanel('body', heading='Inhalt')
    ]

    child_page_types = [SingleEvent]
