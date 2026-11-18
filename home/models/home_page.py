from wagtail.admin.panels.field_panel import FieldPanel
from wagtail.fields import StreamField
from wagtail.models import Page

from home.models.common import (
    BlogListBlock,
    CommonContextMixin,
    SidebarPromotionMixin,
    create_multi_column_block,
    gen_body_content,
)

home_body_content = [*gen_body_content, ("blog_list", BlogListBlock())]


class HomePage(CommonContextMixin, SidebarPromotionMixin, Page):
    body = StreamField(
        [
            *home_body_content,
            (
                "multi_column",
                create_multi_column_block(content_blocks=home_body_content)(),
            ),
        ],
        default=[],
    )

    content_panels = Page.content_panels + [FieldPanel("body", heading="Inhalt")]
    promote_panels = SidebarPromotionMixin.promote_panels

    subpage_types = ["home.HomePage", "home.EventPage", "home.GalleryIndexPage"]
