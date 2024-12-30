import urllib

from django import template
from urllib.parse import urlparse
# import site:
from wagtail.models import Site, Page

register = template.Library()

@register.simple_tag(takes_context=True)
def get_site_root(context: dict) -> Page:
    return Site.find_for_request(context["request"]).root_page

@register.simple_tag(takes_context=True)
def add_active_class(context: dict, menu_url: str)->str:
    menu_path = urlparse(menu_url).path
    current_path = context["request"].path
    if menu_path == current_path:
        return "active"
    else:
        return ""
