from home.models.base import gen_body_content
from home.models.events import SingleEvent


from django.utils.timezone import now
from wagtail.admin.panels.field_panel import FieldPanel
from wagtail.fields import StreamField
from wagtail.models import Page


class HomePage(Page):
    body = StreamField(gen_body_content, default=[])

    content_panels = Page.content_panels + [FieldPanel("body", heading="Inhalt")]

    subpage_types = ["home.HomePage", "home.EventPage", "home.GalleryIndexPage"]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["all_events"] = (
            SingleEvent.objects.live()
            .public()
            .filter(start_time__gte=now())  # Match events at or after the current time
            .order_by("start_time")
        )
        return context