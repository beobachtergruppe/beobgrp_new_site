from django import template

register = template.Library()

@register.inclusion_tag('event_checkbox_style.html')
def event_checkbox_toggle_style(class_suffix: str):
    return {'class_suffix': class_suffix}
