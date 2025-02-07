from datetime import date, datetime, timedelta
from functools import cached_property
import hashlib
import logging
from copy import deepcopy
import textwrap
from typing import Tuple

from django.db.models import TextChoices
from django.db.models.fields import DateTimeField, CharField, BooleanField
from django.db.models.fields.files import ImageField
from django.utils.text import slugify
from django.utils.timezone import localtime, now
from wagtail.admin.forms.pages import WagtailAdminPageForm
from wagtail.admin.panels.field_panel import FieldPanel
from wagtail.blocks.field_block import RichTextBlock, CharBlock, ChoiceBlock, FieldBlock
from wagtail.blocks.struct_block import StructBlock
from wagtail.fields import StreamField, RichTextField
from wagtail.images.blocks import ImageChooserBlock
from wagtail.models import Page

from beobgrp_site.utils.email import create_email_link

logger = logging.getLogger(__name__)

gen_body_content: list[Tuple[str, FieldBlock]] = [
    ("h1", CharBlock(form_classname="h1", label="Kopfzeile 1")),
    ("h2", CharBlock(form_classname="h2", label="Kopfzeile 2")),
    ("h3", CharBlock(form_classname="h3", label="Kopfzeile 3")),
    ("paragraph", RichTextBlock()),
    ("image", ImageChooserBlock()),
]


class HomePage(Page):
    body = StreamField(gen_body_content, default=[])

    content_panels = Page.content_panels + [FieldPanel("body", heading="Inhalt")]


class EventTypes(TextChoices):
    TALK = "Vortrag", "Vortrag"
    HYBRID = "Hybride Vortrag", "Hybride Vortrag"
    ONLINE = "Online Vortrag", "Online Vortrag"
    OBSERVE = "Beobachtungsabend", "Beobachtungsabend"
    EXCURSION = "Ausflug", "Ausflug"


class SingleEventForm(WagtailAdminPageForm):

    def clean(self):
        if not self.data.get("title"):
            self.data = self.data.copy()
            self.data["title"] = "Default Placeholder Title"
            self.data["slug"] = "default-placeholder-slug"

        cleaned_data = super().clean()
        return cleaned_data


class SingleEvent(Page):
    start_time = DateTimeField()
    event_type = CharField(choices=EventTypes.choices)
    event_title = CharField(max_length=100, default="")
    location = CharField(max_length=120, default="Deutsches Museum")
    referent = CharField(max_length=120, default="")
    abstract = RichTextField(max_length=800, default="")
    image = ImageField(blank=True)
    cancelled = BooleanField(default=False)
    booked_out = BooleanField(default=False)
    needs_reservation = BooleanField(default=True)

    def __post_init__(self):
        self.title.editable = False

    content_panels = Page.content_panels + [
        FieldPanel("event_type", heading="Art der Veranstaltung"),
        FieldPanel("event_title", heading="Titel"),
        FieldPanel("needs_reservation", heading="Reservierung erforderlich"),
        FieldPanel("cancelled", heading="Abgesagt"),
        FieldPanel("booked_out", heading="Ausgebucht"),
        FieldPanel("start_time", heading="Zeit"),
        FieldPanel("location", heading="Ort"),
        FieldPanel("referent", heading="Referent"),
        FieldPanel("abstract", heading="Zusammenfassung"),
        FieldPanel("image", heading="Foto")
    ]

    # Override the save method to auto-generate title and slug
    def save(self, *args, **kwargs):
        self.title = _get_default_event_title(self.start_time, self.event_title)
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @cached_property
    def web_id(self) -> str:
        hash_code = hashlib.sha256(str(self).encode("utf-8")).hexdigest()
        return hash_code[:8]

    @cached_property
    def first_reservation_date(self) -> date:
        return self.start_time.date() - timedelta(weeks=4)

    @cached_property
    def is_reservable(self) -> bool:
        """
        An event is reservable up to 4 weeks in advance if not cancelled or booked out
        """
        is_open = not self.cancelled and not self.booked_out
        return date.today() >= self.first_reservation_date and is_open

    @cached_property
    def reservation_mailto_link(self) -> str:
        return create_email_link(
            email_address="reservierung@beobachtergruppe.de",
            subject=f"Anmeldung für den Vortrag am {self.start_time:%d.%m.%y} ({self.event_title})",
            body=textwrap.dedent(f"""
                  Liebe Beobachtergruppe,
                  
                  bitte um Anmeldung zum folgenden Vortrag:
                  
                    {self.event_title}
                    {self.referent}
                  
                    am {self.start_time:%A, den %d.%m.%y} um {self.start_time:%H:%M} Uhr
                   
                  Name, Vorname: ... 
                  Anzahl Personen: ...
                  
                  Mit freundlichen Grüßen
                  ...
            """)
        )

    base_form_class = SingleEventForm


def _get_default_event_title(start_time, event_title):
    if start_time and event_title:
        formatted_start_time = localtime(start_time).strftime("%Y-%m-%d %H:%M")
        return f"{formatted_start_time} - {event_title}"
    return "Default Title"


class EventListBlock(StructBlock):
    event_type = ChoiceBlock(
        choices=EventTypes.choices,
        required=True,
        label="Art der Veranstaltung",
        help_text="Liste von Veranstaltungen",
    )

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context)

        if parent_context is not None:
            # Get the current page (parent page)
            parent_page = parent_context["page"]

            # Query child pages of the parent that are of type SingleEvent
            events = (
                SingleEvent.objects.child_of(parent_page)
                .live()
                .filter(
                    event_type=value["event_type"],  # Match the event type
                    start_time__gte=now(),  # Match events at or after the current time
                )
                .order_by("start_time")
            )  # Order by start time

            # Add events to the context
            context["events"] = events

        return context

    class Meta:
        template = "blocks/event_list_block.html"  # Template for rendering the block


blocks_for_event_body = deepcopy(gen_body_content)
blocks_for_event_body.append(("event_list", EventListBlock()))  # type: ignore


class EventPage(Page):
    body = StreamField(blocks_for_event_body, default=[])

    content_panels = Page.content_panels + [FieldPanel("body", heading="Inhalt")]

    child_page_types = [SingleEvent]
