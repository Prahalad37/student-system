from django import template

register = template.Library()


@register.simple_tag
def pagination_query(request, page_number):
    """Return query string for pagination, preserving existing GET params."""
    get = request.GET.copy()
    get['page'] = page_number
    return get.urlencode()
