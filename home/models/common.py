from __future__ import annotations
from typing import TYPE_CHECKING, Tuple

from wagtail.blocks import Block
from wagtail.blocks.field_block import RichTextBlock, CharBlock, FieldBlock, URLBlock, ChoiceBlock
from wagtail.blocks.struct_block import StructBlock
from wagtail.images.blocks import ImageChooserBlock

if TYPE_CHECKING:
    from django.http import HttpRequest


class ImageWithCaptionBlock(StructBlock):
    image = ImageChooserBlock(label="Bild")
    caption = CharBlock(
        required=False, 
        max_length=255, 
        label="Bildunterschrift",
        help_text="Optional text to display with the image"
    )
    caption_position = ChoiceBlock(
        choices=[
            ('top', 'Oben'),
            ('bottom', 'Unten'),
            ('left', 'Links'),
            ('right', 'Rechts'),
        ],
        default='bottom',
        label="Position der Bildunterschrift"
    )
    link = URLBlock(
        required=False,
        label="Optional Link",
        help_text="Optional URL to link the image to (external links only)"
    )

    class Meta: # type: ignore[misc]
        icon = "image"
        label = "Bild mit Bildunterschrift"
        template = "blocks/image_with_caption.html"


gen_body_content: list[Tuple[str, Block]] = [
    ("h1", CharBlock(form_classname="h1", label="Kopfzeile 1")),
    ("h2", CharBlock(form_classname="h2", label="Kopfzeile 2")),
    ("h3", CharBlock(form_classname="h3", label="Kopfzeile 3")),
    ("paragraph", RichTextBlock()),
    ("image", ImageChooserBlock()),
    ("image_with_caption", ImageWithCaptionBlock()),
]


class CommonContextMixin:
    """
    Mixin for pages that can have events.
    This mixin should be used with Wagtail Page classes.
    """

    def _get_upcoming_events(self):
        from home.models.events import SingleEvent
        from django.utils.timezone import now

        return (
            SingleEvent.objects.live()  # type: ignore[attr-defined]
            .public()
            .filter(start_time__gte=now())  # Match events at or after the current time
            .order_by("start_time")[:2]
        )
    
    def get_context(self, request: "HttpRequest", *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)  # type: ignore[misc]
        context["upcoming_events"] = self._get_upcoming_events()
        return context
