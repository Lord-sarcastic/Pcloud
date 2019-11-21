from django import template
import re
register = template.Library()

@register.filter
def qslice(queryset, bounds):
    bounds = split(bounds)
    if (len(bounds) > 3) or (len(bounds) < 0):
        return None
    else:
        try:
            for i in bounds:
                int(i)
        except:
            return None
        if len(bounds) == 1:
            return queryset[int(bounds[0])]
        if len(bounds) == 2:
            return queryset[int(bounds[0]):int(bounds[1])]
        else:
            return queryset[int(bounds[0]):int(bounds[1]):int(bounds[2])]

@register.filter
def addclass(value, arg):
    return value.as_widget(attrs={'class': arg})

@register.filter
def filename(value, arg):
    return value.split(arg)[-1]