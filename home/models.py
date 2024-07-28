from wagtail.admin.panels.field_panel import FieldPanel
from wagtail.blocks.field_block import RichTextBlock, CharBlock
from wagtail.fields import StreamField
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
        FieldPanel('body')
    ]
