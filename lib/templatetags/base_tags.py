from django import template
from django.template.defaultfilters import safe

from blog.models import Sponsor, Footer

from wagtail.core.models import Page
from markdown import markdown

register = template.Library()


@register.filter()
def markdownify(value):
    return markdown(value)


@register.simple_tag(takes_context=True)
def is_nightmode(context):
    user = context['request'].user
    try:
        if user.compsocuser:
            return user.compsocuser.nightmode_on or bool(context['request'].session.get('night_mode', default=False))
        else:
            return bool(context['request'].session.get('night_mode', default=False))
    except AttributeError:
        return bool(context['request'].session.get('night_mode', default=False))


@register.inclusion_tag('lib/tags/sponsor_homepage.html', takes_context=True)
def sponsor_homepage(context):
    return {
        'sponsors': Sponsor.objects.filter(primary_sponsor=True).all(),
        'request': context['request'],
    }


@register.inclusion_tag('lib/tags/sponsor_sidebar.html', takes_context=True)
def sponsor_sidebar(context):
    return {
        'sponsors': Sponsor.objects.filter(primary_sponsor=True).all(),
        'request': context['request'],
    }


@register.simple_tag(takes_context=True)
def get_site_root(context):
    # NB this returns a core.Page, not the implementation-specific model used
    # so object-comparison to self will return false as objects would differ
    return context['request'].site.root_page


# Retrieves the top menu items
@register.inclusion_tag('lib/tags/top_menu.html', takes_context=True)
def top_menu(context, parent, calling_page=None):
    menuitems = parent.get_children().live().in_menu()
    for menuitem in menuitems:
        # We don't directly check if calling_page is None since the template
        # engine can pass an empty string to calling_page
        # if the variable passed as calling_page does not exist.
        menuitem.active = (calling_page.startswith(menuitem.url)
                           if calling_page else False)
    if context['request'].user.is_authenticated():
        has_newsletter_perms = context['request'].user.has_perms(
            ['newsletter.create_mail', 'newsletter.change_mail', 'newsletter.delete_mail'])
    else:
        has_newsletter_perms = False

    return {
        'calling_page': calling_page,
        'menuitems': menuitems,
        'is_home': calling_page == u'/',
        'has_newsletter_perms': has_newsletter_perms,
        # required by the pageurl tag that we want to use within this template
        'request': context['request'],
    }


# Retrieves the footer sitemap items
@register.inclusion_tag('lib/tags/footer.html', takes_context=True)
def footer(context, parent):
    if Footer.objects.first():
        return {
            'menuitems': parent.get_children().live().in_menu(),
            'facebook_url': Footer.objects.first().facebook_url,
            'twitch_url': Footer.objects.first().twitch_url,
            'twitter_url': Footer.objects.first().twitter_url,
            'privacy_policy_url': Footer.objects.first().privacy_policy_url,
            # required by the pageurl tag that we want to use within this template
            'request': context['request'],
        }
    else:
        return {
            # required by the pageurl tag that we want to use within this template
            'request': context['request'],
        }


@register.inclusion_tag('lib/tags/breadcrumbs.html', takes_context=True)
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
        'request': context['request'],
    }
