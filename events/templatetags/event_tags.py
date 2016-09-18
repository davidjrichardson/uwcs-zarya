from django import template
from wagtail.wagtailcore.models import Page

register = template.Library()


@register.inclusion_tag('events/tags/event_breadcrumbs.html', takes_context=True)
def breadcrumbs(context):
    self = context.get('self')
    if self is None or self.depth <= 2:
        # When on the home page, displaying breadcrumbs is irrelevant.
        ancestors = ()
    else:
        ancestors = Page.objects.ancestor_of(
            self, inclusive=True).filter(depth__gt=2)
    return {
        'ancestors': ancestors,
        'date': self.start,
        'request': context['request'],
    }


@register.inclusion_tag('events/tags/event_sidebar.html', takes_context=True)
def sidebar(context, show_sponsor=False, display_first=False):
    return {
        'show_sponsor': show_sponsor,
        'display_first': display_first,
        # required by the pageurl tag that we want to use within this template
        'request': context['request'],
    }


@register.filter
def subtract(value, arg):
    return value - arg
