from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def get_query_parameters(context, **kwargs):
    query = context["request"].GET.copy()
    for key, value in kwargs.items():
        query[key] = value
    return query.urlencode()
