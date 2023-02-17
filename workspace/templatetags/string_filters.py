from django import template

register = template.Library()

@register.simple_tag
def get_actual_name(filename):
    pos = filename.rfind("_")
    return filename[:pos]

@register.filter()
def to_int(value):
    return int(value)