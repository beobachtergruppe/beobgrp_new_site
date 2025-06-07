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


