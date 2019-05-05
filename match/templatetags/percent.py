from django import template

register = template.Library()

@register.filter
def percent(value):
    return '{0:.4}'.format(value*100)