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
from django.utils.timezone import localtime, now, make_aware, is_naive
from django.utils.dateparse import parse_datetime
from wagtail.admin.forms.pages import WagtailAdminPageForm
from wagtail.blocks.field_block import MultipleChoiceBlock
from wagtail.blocks.struct_block import StructBlock
from wagtail.fields import StreamField


from home.models.common import (
    CommonContextMixin,
    SidebarPromotionMixin,
    gen_body_content,
    create_multi_column_block,
)

logger = logging.getLogger(__name__)


class EventTypes(TextChoices):
    TALK = "Vortrag", "Vortrag"
    HYBRID = "Hybride Vortrag", "Hybride Vortrag"
    ONLINE = "Online Vortrag", "Online Vortrag"
    OBSERVE = "Beobachtungsabend", "Beobachtungsabend"
    EXCURSION = "Ausflug", "Ausflug"


# Form field constraints (must not exceed DB model max_length values)
EVENT_TITLE_MAX_LENGTH = 80   # DB max_length: 140
ABSTRACT_MAX_LENGTH = 600     # DB max_length: 800

# Ensure form constraints don't exceed DB model constraints
assert EVENT_TITLE_MAX_LENGTH <= 140, "EVENT_TITLE_MAX_LENGTH must not exceed DB model max_length (140)"
assert ABSTRACT_MAX_LENGTH <= 800, "ABSTRACT_MAX_LENGTH must not exceed DB model max_length (800)"

class SingleEventForm(WagtailAdminPageForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add max_length to form fields to show character counter in admin
        if 'event_title' in self.fields:
            self.fields['event_title'].max_length = EVENT_TITLE_MAX_LENGTH
        if 'abstract' in self.fields:
            self.fields['abstract'].max_length = ABSTRACT_MAX_LENGTH
            # RichTextArea stores max_length in widget.options for the JS character counter
            if hasattr(self.fields['abstract'].widget, 'options'):
                self.fields['abstract'].widget.options['max_length'] = ABSTRACT_MAX_LENGTH
    
    def clean(self):
        # Step 1: Handle OBSERVE event default title before any validation
        event_type = self.data.get("event_type")
        event_title = self.data.get("event_title", "")
        
        if event_type == EventTypes.OBSERVE and not event_title:
            event_title = _get_default_event_title(event_type)
            # Update form data so super().clean() sees the default title
            if not self.data.get("event_title"):
                self.data = self.data.copy()
                self.data["event_title"] = event_title
        
        # Step 2: Generate and set title/slug BEFORE calling super().clean()
        # This ensures Wagtail's slug validation sees a valid slug
        start_time = self.data.get("start_time")
        if start_time and event_title:
            try:
                generated_title = _get_page_title(start_time, event_title)
                if not self.data.get("title"):
                    self.data = self.data.copy()
                    self.data["title"] = generated_title
                    self.data["slug"] = slugify(generated_title)
            except ValueError:
                # If generation fails, provide fallback so Wagtail validation doesn't fail
                if not self.data.get("slug"):
                    self.data = self.data.copy()
                    self.data["slug"] = "event"
        else:
            # Ensure slug is set even if we can't generate title yet
            if not self.data.get("slug"):
                self.data = self.data.copy()
                self.data["slug"] = "event"
        
        # Step 3: Now call super().clean() with valid title/slug in place
        cleaned_data = super().clean()
        
        # Step 4: Perform custom validation on cleaned data
        event_type = cleaned_data.get("event_type")
        event_title = cleaned_data.get("event_title", "")
        referent = cleaned_data.get("referent", "")
        abstract = cleaned_data.get("abstract", "")
        
        # Validate event_title length (character limit for new/updated titles)
        if event_title and len(event_title) > EVENT_TITLE_MAX_LENGTH:
            self.add_error("event_title", f"Titel darf maximal {EVENT_TITLE_MAX_LENGTH} Zeichen lang sein.")
        
        # Validate abstract length (character limit for new/updated abstracts)
        if abstract and len(abstract) > ABSTRACT_MAX_LENGTH:
            self.add_error("abstract", f"Zusammenfassung darf maximal {ABSTRACT_MAX_LENGTH} Zeichen lang sein.")
        
        # For non-OBSERVE events, title, referent, and abstract are required
        if event_type != EventTypes.OBSERVE:
            if not event_title:
                self.add_error("event_title", "Titel ist erforderlich für diesen Veranstaltungstyp.")
            if not referent:
                self.add_error("referent", "Referent ist erforderlich für diesen Veranstaltungstyp.")
            if not abstract:
                self.add_error("abstract", "Zusammenfassung ist erforderlich für diesen Veranstaltungstyp.")
        
        return cleaned_data


def _get_page_title(start_time, event_title):
    if not start_time:
        raise ValueError("start_time is required to generate page title")
    if not event_title:
        raise ValueError("event_title is required to generate page title")
    
    if isinstance(start_time, str):
        start_time = parse_datetime(start_time)
        if start_time is None:
            raise ValueError(f"Cannot parse start_time string")
    if is_naive(start_time):
        start_time = make_aware(start_time)
    
    formatted_start_time = localtime(start_time).strftime("%Y-%m-%d %H:%M")
    return f"{formatted_start_time} - {event_title}"


def _get_default_event_title(event_type):
    """Get the default event title for a specific event type."""
    if event_type == EventTypes.OBSERVE:
        return "Beobachtungsabend"
    return ""


class SingleEvent(Page):
    start_time: DateTimeField = DateTimeField()
    event_type: CharField = CharField(choices=EventTypes.choices)
    event_title: CharField = CharField(max_length=140, default="", blank=True)
    location: CharField = CharField(max_length=120, default="Deutsches Museum")
    referent: CharField = CharField(max_length=120, default="", blank=True)
    abstract: RichTextField = RichTextField(max_length=800, default="", blank=True)
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

    content_panels = [
        FieldPanel("event_type", heading="Art der Veranstaltung"),
        FieldPanel("start_time", heading="Zeit"),
        FieldPanel("event_title", heading="Titel (optional für Beobachtungsabend)", help_text=f"Max. {EVENT_TITLE_MAX_LENGTH} Zeichen"),
        FieldPanel("needs_reservation", heading="Reservierung erforderlich"),
        FieldPanel("cancelled", heading="Abgesagt"),
        FieldPanel("booked_out", heading="Ausgebucht"),
        FieldPanel("location", heading="Ort", help_text=f"Max. 120 Zeichen"),
        FieldPanel("referent", heading="Referent (optional für Beobachtungsabend)", help_text=f"Max. 120 Zeichen"),
        FieldPanel("abstract", heading="Zusammenfassung (optional für Beobachtungsabend)", help_text=f"Max. {ABSTRACT_MAX_LENGTH} Zeichen"),
        FieldPanel("image", heading="Foto"),
    ]

    def clean(self):
        # Called by _post_clean() after all form values are applied to the instance.
        # At this point self.start_time already has the newly submitted value, so the
        # generated title and slug always reflect the current data.
        try:
            self.title = _get_page_title(self.start_time, self.event_title)
            self.slug = slugify(self.title)
        except ValueError as e:
            logger.error(f"Cannot clean SingleEvent: {e}")
            raise
        super().clean()

    # Keep save() as an additional safety net (e.g. programmatic saves).
    def save(self, *args, **kwargs):
        try:
            self.title = _get_page_title(self.start_time, self.event_title)
            self.slug = slugify(self.title)
        except ValueError as e:
            logger.error(f"Cannot save SingleEvent: {e}")
            raise
        super().save(*args, **kwargs)

    @cached_property
    def web_id(self) -> str:
        hash_code = hashlib.sha256(str(self).encode("utf-8")).hexdigest()
        return hash_code[:8]

    @cached_property
    def first_reservation_date(self) -> date:
        return localtime(self.start_time).date() - timedelta(weeks=4)

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
        # Build body based on whether event has a real title or just the default
        # Use detailed format only for events with custom titles (not auto-assigned defaults)
        has_custom_title = self.event_title and self.event_title != _get_default_event_title(self.event_type)
        
        if has_custom_title:
            # Detailed format for events with titles (Vortrag, Ausflug, etc.)
            referent_line = (
                f"  {self.referent}\n"
                if self.referent and self.event_type in [
                    EventTypes.TALK,
                    EventTypes.HYBRID,
                    EventTypes.ONLINE,
                ]
                else ""
            )
            
            location_line = (
                f"  Ort: {self.location}\n"
                if self.location and self.event_type in [
                    EventTypes.TALK,
                    EventTypes.HYBRID,
                    EventTypes.OBSERVE,
                    EventTypes.EXCURSION,
                ]
                else ""
            )
            
            body = textwrap.dedent(f"""
                Liebe Beobachtergruppe,
                
                bitte um Anmeldung zum folgenden {self.event_type}:
                
                  {self.event_title}
                {referent_line}{location_line}
                am {self.start_time:%A, den %d.%m.%y} um {self.start_time:%H:%M} Uhr
                
                Name, Vorname: ...
                Anzahl Personen: ...
                
                Mit freundlichen Grüßen
                ...
            """).strip()
        else:
            # Simple inline format for events without custom titles (e.g., Beobachtungsabend)
            location_str = f"im {self.location}" if self.location else ""
            body = textwrap.dedent(f"""
                Liebe Beobachtergruppe,
                
                bitte um Anmeldung zum {self.event_type} {location_str} am {self.start_time:%A, den %d.%m.%y} um {self.start_time:%H:%M} Uhr.
                
                Name, Vorname: ...
                Anzahl Personen: ...
                
                Mit freundlichen Grüßen
                ...
            """).strip()
        
        # Build subject with event type
        subject_prefix = f"{self.event_type} am {self.start_time:%d.%m.%y}"
        subject = (
            f"Anmeldung für {subject_prefix} ({self.event_title})"
            if has_custom_title
            else f"Anmeldung für {subject_prefix}"
        )
        
        return create_email_link(
            email_address="reservierung@beobachtergruppe.de",
            subject=subject,
            body=body,
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

            events_qs = (
                SingleEvent.objects.child_of(parent_page)
                .live()
                .filter(start_time__gte=now())
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


class EventPage(CommonContextMixin, SidebarPromotionMixin, Page):
    body = StreamField(
        [
            *blocks_for_event_body,
            (
                "multi_column",
                create_multi_column_block(content_blocks=blocks_for_event_body)(),
            ),
        ],
        default=[],
    )

    content_panels = Page.content_panels + [FieldPanel("body", heading="Inhalt")]
    promote_panels = SidebarPromotionMixin.promote_panels

    subpage_types = ["home.SingleEvent", "home.EventPage", "home.GalleryPage"]
