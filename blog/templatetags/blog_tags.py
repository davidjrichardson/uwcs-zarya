from datetime import date, datetime
from django import template
from django.conf import settings

from blog.models import BlogPage, BlogIndexPage, CodeBlock

register = template.Library()


@register.inclusion_tag(
    'blog/tags/blog_sidebar.html',
    takes_context = True
)
def blog_sidebar(context, show_sponsor=False, show_archives=False, show_events=False):
    blog_index = BlogIndexPage.objects.live().in_menu().first()

    if show_archives:
        # TODO: Order in descending date order for months
        archives = dict()
        for blog in BlogPage.objects.live().order_by('-date'):
            archives.setdefault(blog.date.year, {}).setdefault(blog.date.month, []).append(blog)
    else:
        archives = None

    if show_events:
        # TODO: Implement upcoming events
        events = ["Foo"]
    else:
        events = None

    return {
        'blog_index': blog_index,
        'archives': archives,
        'events': events,
        'show_sponsor': show_sponsor,
        # required by the pageurl tag that we want to use within this template
        'request': context['request'],
    }


# Blog feed for home page
@register.inclusion_tag(
    'blog/tags/blog_listing_homepage.html',
    takes_context=True
)
def blog_listing_homepage(context, count=5):
    blogs = BlogPage.objects.live().order_by('-date')
    blog_index = BlogIndexPage.objects.live().in_menu().first()

    # TODO: Order in descending date order for months
    archives = dict()
    for blog in blogs:
        archives.setdefault(blog.date.year, {}).setdefault(blog.date.month, []).append(blog)

    return {
        'blogs': blogs[:count],
        'blog_index': blog_index,
        'archives': archives,
        # required by the pageurl tag that we want to use within this template
        'request': context['request'],
    }


# Event feed for home page
@register.inclusion_tag(
    'blog/tags/event_listing_homepage.html',
    takes_context=True
)
def event_listing_homepage(context, count=4):
    # TODO: Get upcoming events
    return {
        'events': [],
        # required by the pageurl tag that we want to use within this template
        'request': context['request'],
    }


@register.inclusion_tag(
    'blog/tags/search_filters.html',
    takes_context=True
)
def search_filters(context):
    archive_date = context['request'].GET.get('date')

    if archive_date:
        archive_date = datetime.strftime(
            datetime.strptime(context['request'].GET.get('date'), '%Y-%m'), '%B %Y')

    return {
        'archive_date': archive_date,
        'tag': context['request'].GET.get('tag'),
        # required by the pageurl tag that we want to use within this template
        'request': context['request'],
    }


@register.filter
def get_code_language(language):
    return dict(CodeBlock.LANGUAGE_CHOICES)[language]


@register.filter
def to_month_str(value):
    return {
        1: 'January',
        2: 'February',
        3: 'March',
        4: 'April',
        5: 'May',
        6: 'June',
        7: 'July',
        8: 'August',
        9: 'September',
        10: 'October',
        11: 'November',
        12: 'December',
    }[value]
