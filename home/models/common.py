from __future__ import annotations
from typing import TYPE_CHECKING, Tuple

from wagtail.blocks import Block
from wagtail.blocks.field_block import RichTextBlock, CharBlock, FieldBlock, URLBlock, ChoiceBlock
from wagtail.blocks.struct_block import StructBlock, StructBlockValidationError
from django.core.exceptions import ValidationError
from wagtail.images.blocks import ImageChooserBlock
from wagtail.blocks import PageChooserBlock

if TYPE_CHECKING:
    from django.http import HttpRequest


class LinkBlock(StructBlock):
    """
    A flexible link block that supports both internal and external links.
    """
    link_type = ChoiceBlock(
        choices=[
            ('none', 'Kein Link'),
            ('internal', 'Interne Seite'),
            ('external', 'Externe URL'),
        ],
        default='none',
        label="Link-Typ"
    )
    internal_page = PageChooserBlock(
        required=False,
        label="Interne Seite",
        help_text="Wählen Sie eine Seite aus dieser Website"
    )
    external_url = URLBlock(
        required=False,
        label="Externe URL",
        help_text="Geben Sie eine vollständige URL ein (z.B. https://example.com)"
    )
    
    def clean(self, value):
        """
        Validate that when link_type is not 'none', the corresponding URL is provided.
        """
        errors = {}

        if isinstance(value, dict):
            link_type = value.get('link_type')
            internal_page = value.get('internal_page')
            external_url = value.get('external_url')

            # If link_type is 'internal', internal_page must be provided
            if link_type == 'internal' and not internal_page:
                errors['internal_page'] = ValidationError('Bitte wählen Sie eine Seite aus, wenn Sie "Interne Seite" als Link-Typ ausgewählt haben.')

            # If link_type is 'external', external_url must be provided
            if link_type == 'external' and not external_url:
                errors['external_url'] = ValidationError('Bitte geben Sie eine URL ein, wenn Sie "Externe URL" als Link-Typ ausgewählt haben.')

            # If link_type is None and a link is provided
            if link_type is None and (internal_page or external_url):
                errors['link_type'] = ValidationError('Bitte wählen Sie einen Link-Typ aus, wenn Sie einen Link angeben.')

        if errors:
            raise StructBlockValidationError(errors)

        return super().clean(value)
    
    class Meta: # type: ignore[misc]
        icon = "link"
        label = "Link"


class ImageWithCaptionBlock(StructBlock):
    image = ImageChooserBlock(label="Bild")
    caption = RichTextBlock(
        required=False,
        label="Bildunterschrift",
        help_text="Optional formatted text to display with the image"
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
    link = LinkBlock(
        label="Optional Link",
        help_text="Optionaler Link für das Bild (interne Seite oder externe URL)"
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
