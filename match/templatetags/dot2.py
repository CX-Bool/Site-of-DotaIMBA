from django import template
import math
register = template.Library()

@register.filter
def dot2(value):
    return '<strong>%d</strong>'%int(math.floor(value))+'{0:.2f}'.format(math.modf(value)[0])[1:]