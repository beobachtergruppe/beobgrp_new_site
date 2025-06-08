from beobgrp_site.templatetags.navigation_tags import get_site_root
from home.models.common import CommonContextMixin, gen_body_content
from home.models.events import SingleEvent


from django.utils.timezone import now
from wagtail.admin.panels.field_panel import FieldPanel
from wagtail.fields import StreamField
from wagtail.models import Page, Site


class HomePage(CommonContextMixin,Page):
    body = StreamField(gen_body_content, default=[])

    content_panels = Page.content_panels + [FieldPanel("body", heading="Inhalt")]

    subpage_types = ["home.HomePage", "home.EventPage", "home.GalleryIndexPage"]
