from typing import Tuple

from django.db.models import TextChoices
from django.db.models.fields import DateTimeField, CharField, BooleanField
from django.db.models.fields.files import ImageField
from django.utils.timezone import localtime, now
from wagtail.admin.forms.pages import WagtailAdminPageForm
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

class SingleEventForm(WagtailAdminPageForm):
    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        event_title = cleaned_data.get('event_title')

        if start_time:
            # Format start_time into 'YYYY-MM-DD HH:MM'
            formatted_start_time = localtime(start_time).strftime('%Y-%m-%d %H:%M')
            # Auto-generate the title
            cleaned_data['title'] = f"{formatted_start_time} - {event_title or 'Event'}"
        return cleaned_data

class SingleEvent(Page):
    start_time = DateTimeField()
    event_type = CharField(choices=EventTypes)
    event_title = CharField(max_length=100,default='')
    location = CharField(max_length=120, default="Deutsches Museum")
    referent = CharField(max_length=120)
    abstract = RichTextField(max_length=800)
    image = ImageField(blank=True)
    cancelled = BooleanField(default=False)
    booked_out = BooleanField(default=False)

    base_form_class = SingleEventForm

    # Override the save method to update the title
    def save(self, *args, **kwargs):
        if self.start_time:
            self.title = f"{localtime(self.start_time).strftime('%Y-%m-%d %H:%M')} - {self.event_title}"
        super().save(*args, **kwargs)

    content_panels = Page.content_panels + [
        FieldPanel('start_time', heading='Zeit'),
        FieldPanel('event_type', heading='Art der Veranstaltung'),
        FieldPanel('event_title', heading='Titel'),
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

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context)

        if parent_context is not None:
            # Get the current page (parent page)
            parent_page = parent_context['page']

            # Query child pages of the parent that are of type SingleEvent
            events = SingleEvent.objects.child_of(parent_page).live().filter(
                event_type=value['event_type'],  # Match the event type
                start_time__gte=now()  # Match events at or after the current time
            ).order_by('start_time')  # Order by start time

            # Add events to the context
            context['events'] = events

        return context

    class Meta:
        template = "blocks/event_list_block.html"  # Template for rendering the block

blocks_for_event_body = deepcopy(gen_body_content)
blocks_for_event_body.append(('event_list', EventListBlock())) # type: ignore

class EventPage(Page):
    body = StreamField(blocks_for_event_body, default=[])

    content_panels = Page.content_panels + [
        FieldPanel('body', heading='Inhalt')
    ]

    child_page_types = [SingleEvent]
