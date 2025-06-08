from __future__ import annotations
from typing import Tuple

from wagtail.blocks.field_block import RichTextBlock, CharBlock, FieldBlock
from wagtail.images.blocks import ImageChooserBlock


gen_body_content: list[Tuple[str, FieldBlock]] = [
    ("h1", CharBlock(form_classname="h1", label="Kopfzeile 1")),
    ("h2", CharBlock(form_classname="h2", label="Kopfzeile 2")),
    ("h3", CharBlock(form_classname="h3", label="Kopfzeile 3")),
    ("paragraph", RichTextBlock()),
    ("image", ImageChooserBlock()),
]


class CommonContextMixin:
    """
    Mixin for pages that can have events.
    """

    def _get_upcoming_events(self):
        from home.models.events import SingleEvent
        from django.utils.timezone import now

        return (
            SingleEvent.objects.live()
            .public()
            .filter(start_time__gte=now())  # Match events at or after the current time
            .order_by("start_time")[:2]
        )
    
    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["upcoming_events"] = self._get_upcoming_events()
        return context