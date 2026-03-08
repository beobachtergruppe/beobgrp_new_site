from home.models.common import CommonContextMixin, gen_body_content, create_multi_column_block


from wagtail.admin.panels.field_panel import FieldPanel
from wagtail.fields import StreamField
from wagtail.models import Page


class HomePage(CommonContextMixin,Page):
    body = StreamField([
        *gen_body_content,
        ("multi_column", create_multi_column_block(content_blocks=gen_body_content)()),
    ], default=[])
    content_panels = Page.content_panels + [FieldPanel("body", heading="Inhalt")]

    subpage_types = ["home.HomePage", "home.EventPage", "home.GalleryIndexPage"]
