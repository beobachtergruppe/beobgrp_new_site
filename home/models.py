from typing import Tuple

from django.db.models import TextChoices
from django.db.models.fields import DateTimeField, CharField, BooleanField
from django.db.models.fields.files import ImageField
from wagtail.admin.panels.field_panel import FieldPanel
from wagtail.blocks.field_block import RichTextBlock, CharBlock, ChoiceBlock, FieldBlock
from wagtail.blocks.struct_block import StructBlock
from wagtail.fields import StreamField, RichTextField
from wagtail.images.blocks import ImageChooserBlock

from wagtail.models import Page
from copy import deepcopy

gen_body_content: list[Tuple[str, FieldBlock]] = [
    ('h1', CharBlock(form_classname='h1', label='Kopfzeile 1')),
    ('h2', CharBlock(form_classname='h2', label='Kopfzeile 2')),
    ('h3', CharBlock(form_classname='h3', label='Kopfzeile 3')),
    ('paragraph', RichTextBlock()),
    ('image', ImageChooserBlock())
]

class HomePage(Page):
    body = StreamField(gen_body_content, default=[])

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

blocks_for_event_body = deepcopy(gen_body_content)
blocks_for_event_body.append(('event_list', EventListBlock())) # type: ignore

class EventPage(Page):
    body = StreamField(blocks_for_event_body, default=[])

    content_panels = Page.content_panels + [
        FieldPanel('body', heading='Inhalt')
    ]

    child_page_types = [SingleEvent]
