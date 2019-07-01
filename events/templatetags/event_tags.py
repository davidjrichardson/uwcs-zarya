from datetime import date, timedelta

from collections import OrderedDict

from django import template
from wagtail.core.models import Page
from events.models import EventsArchivePage

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


@register.inclusion_tag('events/tags/event_archive_breadcrumbs.html', takes_context=True)
def archive_breadcrumbs(context):
    self = context.get('self')
    if self is None or self.depth <= 2:
        # When on the home page, displaying breadcrumbs is irrelevant.
        ancestors = ()
    else:
        ancestors = Page.objects.ancestor_of(
            self, inclusive=True).filter(depth__gt=2)
    return {
        'ancestors': ancestors,
        'request': context['request'],
    }


@register.inclusion_tag('events/tags/event_sidebar.html', takes_context=True)
def sidebar(context, show_sponsor=False, display_first=False, show_archive_link=False):
    archive_page = EventsArchivePage.objects.first() if show_archive_link else None

    return {
        'show_sponsor': show_sponsor,
        'display_first': display_first,
        'archive_page': archive_page,
        # required by the pageurl tag that we want to use within this template
        'request': context['request'],
    }


@register.inclusion_tag('events/tags/event_archive_sidebar.html', takes_context=True)
def archive_sidebar(context, calling_page, show_sponsor=False, display_first=False):
    events = calling_page.archive_events
    archives = OrderedDict()

    for event in events:
        archives.setdefault(event.start.year, {}).setdefault(event.start.month, []).append(event)

    return {
        'show_sponsor': show_sponsor,
        'display_first': display_first,
        'archives': archives,
        'archive_index': calling_page,
        # required by the pageurl tag that we want to use within this template
        'request': context['request'],
    }


@register.filter
def first_monday(event_date):
    year = event_date.isocalendar()[0]
    week = event_date.isocalendar()[1]
    d = date(year, 1, 4)  # The Jan 4th must be in week 1  according to ISO
    return d + timedelta(weeks=(week - 1), days=-d.weekday())


@register.filter
def subtract(value, arg):
    return value - arg
