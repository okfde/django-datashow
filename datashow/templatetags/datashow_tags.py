import markdown
from django import template
from django.utils.encoding import force_str
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag(takes_context=True)
def querystring(context, key=None, value=None):
    request = context["request"]
    if key is None:
        return request.GET.urlencode()
    if value is None:
        query = request.GET.copy()
        query.pop(key, None)
        return query.urlencode()
    if request.GET.get(key) == value:
        return ""
    query = request.GET.copy()
    query[key] = value
    return query.urlencode()


@register.filter(name="listify")
def listify(value):
    return list(value)


@register.filter(name="markdownify")
def markdownify(value):
    return mark_safe(markdown.markdown(force_str(value)))
