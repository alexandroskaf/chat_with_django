from django import template
from django.template.defaulttags import register

register = template.Library()

@register.filter(name='get_bar_color')
def get_bar_color(percentange):
    if percentange < 20:
        return "bg-orange"
    elif 20 <= percentange < 50:
        return "bg-warning"
    elif 50 <= percentange < 80:
        return "bg-primary"
    elif 80 <= percentange <= 99:
        return "bg-info"
    elif percentange == 100:
        return "bg-success"
    else:
        return "bg-gray-600"
        