from beobgrp_site.utils.email import create_email_link

from django.db.models.fields import BooleanField, CharField, DateTimeField
from django.db import models

from django.utils.text import slugify
from wagtail.admin.panels.field_panel import FieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page


import hashlib
import textwrap
from datetime import date, timedelta
from functools import cached_property

import logging
from copy import deepcopy

from django.db.models import TextChoices
from django.utils.timezone import localtime, now
from wagtail.admin.forms.pages import WagtailAdminPageForm
from wagtail.admin.panels.field_panel import FieldPanel
from wagtail.blocks.field_block import MultipleChoiceBlock
from wagtail.blocks.struct_block import StructBlock
from wagtail.fields import StreamField
from wagtail.models import Page


from home.models.common import CommonContextMixin, gen_body_content

logger = logging.getLogger(__name__)


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


def _get_default_event_title(start_time, event_title):
    if start_time and event_title:
        formatted_start_time = localtime(start_time).strftime("%Y-%m-%d %H:%M")
        return f"{formatted_start_time} - {event_title}"
    return "Default Title"


class SingleEvent(Page):
    start_time: DateTimeField = DateTimeField()
    event_type: CharField = CharField(choices=EventTypes.choices)
    event_title: CharField = CharField(max_length=140, default="")
    location: CharField = CharField(max_length=120, default="Deutsches Museum")
    referent: CharField = CharField(max_length=120, default="")
    abstract: RichTextField = RichTextField(max_length=800, default="")
    image: models.ForeignKey = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    cancelled: BooleanField = BooleanField(default=False)
    booked_out: BooleanField = BooleanField(default=False)
    needs_reservation: BooleanField = BooleanField(default=True)

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
        FieldPanel("image", heading="Foto"),
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
    def warning_class(self) -> str:
        if self.cancelled or self.booked_out:
            return "not-available"
        return ""
    
    @cached_property
    def status(self) -> str:
        if self.cancelled:
            return "abgesagt"
        elif self.booked_out:
            return "ausgebucht"
        else:
            return ""

    @cached_property
    def reservation_mailto_link(self) -> str:
        return create_email_link(
            email_address="reservierung@beobachtergruppe.de",
            subject=f"Anmeldung für den Vortrag am {self.start_time:%d.%m.%y} ({self.event_title})",
            body=textwrap.dedent(
                f"""
                  Liebe Beobachtergruppe,
                  
                  bitte um Anmeldung zum folgenden Vortrag:
                  
                    {self.event_title}
                    {self.referent}
                  
                    am {self.start_time:%A, den %d.%m.%y} um {self.start_time:%H:%M} Uhr
                   
                  Name, Vorname: ... 
                  Anzahl Personen: ...
                  
                  Mit freundlichen Grüßen
                  ...
            """
            ),
        )

    base_form_class = SingleEventForm


class EventListBlock(StructBlock):
    event_type = MultipleChoiceBlock(
        choices=EventTypes.choices,
        required=False,
        label="Art der Veranstaltung",
        help_text="Liste von Veranstaltungen",
    )

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context)

        if parent_context is not None:
            # Get the current page (parent page)
            parent_page = parent_context["page"]

            # Query child pages of the parent that are of type SingleEvent
            event_types = value.get("event_type")
            if isinstance(event_types, str):
                event_types = [event_types]
                
            events_qs = SingleEvent.objects.child_of(parent_page).live().filter(
                start_time__gte=now()
            )
            if event_types:
                events_qs = events_qs.filter(event_type__in=event_types)
            events = events_qs.order_by("start_time")

            # Add events to the context
            context["events"] = events

        return context

    class Meta:
        template = "blocks/event_list_block.html"  # Template for rendering the block


blocks_for_event_body = deepcopy(gen_body_content)
blocks_for_event_body.append(("event_list", EventListBlock()))  # type: ignore


class EventPage(CommonContextMixin,Page):
    body = StreamField(blocks_for_event_body, default=[])

    content_panels = Page.content_panels + [FieldPanel("body", heading="Inhalt")]
    
    subpage_types = ["home.SingleEvent","home.EventPage", "home.GalleryPage"]
