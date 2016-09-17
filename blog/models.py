from datetime import datetime, timedelta

from django import forms
from django.utils.safestring import mark_safe
from django.core.paginator import PageNotAnInteger, Paginator, EmptyPage
from django.db import models

from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager

from pygments import highlight
from pygments.formatters import get_formatter_by_name
from pygments.lexers import get_lexer_by_name

from taggit.models import TaggedItemBase

from wagtail.wagtailadmin.edit_handlers import FieldPanel, StreamFieldPanel, MultiFieldPanel
from wagtail.wagtailcore.blocks import TextBlock, StructBlock, StreamBlock, FieldBlock, CharBlock, RichTextBlock, \
    ChoiceBlock
from wagtail.wagtailcore.fields import StreamField, RichTextField
from wagtail.wagtailcore.models import Page
from wagtail.wagtaildocs.blocks import DocumentChooserBlock
from wagtail.wagtailimages.blocks import ImageChooserBlock
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailsnippets.models import register_snippet

from events.models import EventType


@register_snippet
class Footer(models.Model):
    facebook_url = models.URLField(null=True, blank=True)
    twitch_url = models.URLField(null=True, blank=True)

    panels = [
        FieldPanel('facebook_url'),
        FieldPanel('twitch_url'),
    ]

    def __str__(self):
        return 'Footer URLs'


@register_snippet
class Sponsor(models.Model):
    sponsor_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text='This image will be displayed in all sponsor display locations accross the website'
    )
    url = models.URLField(null=True, blank=True)
    text = models.CharField(max_length=255)
    primary_sponsor = models.BooleanField(default=False)

    panels = [
        FieldPanel('text'),
        FieldPanel('primary_sponsor'),
        FieldPanel('url'),
        ImageChooserPanel('sponsor_image'),
    ]

    def __str__(self):
        if self.primary_sponsor:
            return self.text + ' (primary sponsor)'
        else:
            return self.text


# TODO: Remove these - for some reason makemigrations has a fit when these are removed.
class ImageFormatChoiceBlock(FieldBlock):
    field = forms.ChoiceField(choices=(
        ('left', 'Wrap left'), ('right', 'Wrap right'), ('mid', 'Mid width'), ('full', 'Full width'),
    ))


class HTMLAlignmentChoiceBlock(FieldBlock):
    field = forms.ChoiceField(choices=(
        ('normal', 'Normal'), ('full', 'Full width'),
    ))


class PullQuoteBlock(StructBlock):
    quote = TextBlock("quote title")
    attribution = CharBlock()

    class Meta:
        icon = "openquote"


class CodeBlock(StructBlock):
    """
    Code Highlighting Block
    """
    LANGUAGE_CHOICES = (
        ('bash', 'Bash/Shell'),
        ('c', 'C'),
        ('cmake', 'CMake'),
        ('cpp', 'C++'),
        ('csharp', 'C#'),
        ('css', 'CSS'),
        ('go', 'Go'),
        ('haskell', 'Haskell'),
        ('haxe', 'Haxe'),
        ('html', 'HTML'),
        ('java', 'Java'),
        ('js', 'JavaScript'),
        ('json', 'JSON'),
        ('kotlin', 'Kotlin'),
        ('lua', 'Lua'),
        ('make', 'Makefile'),
        ('perl', 'Perl'),
        ('perl6', 'Perl 6'),
        ('php', 'PHP'),
        ('python', 'Python'),
        ('python3', 'Python 3'),
        ('ruby', 'Ruby'),
        ('sql', 'SQL'),
        ('swift', 'Swift'),
        ('xml', 'XML'),
    )

    language = ChoiceBlock(choices=LANGUAGE_CHOICES)
    code = TextBlock()

    class Meta:
        icon = 'code'

    def render(self, value):
        src = value['code'].strip('\n')
        lang = value['language']

        lexer = get_lexer_by_name(lang)
        formatter = get_formatter_by_name(
            'html',
            linenos='table',
            cssclass='code-highlight',
            style='default',
            noclasses=False,
        )
        return mark_safe(highlight(src, lexer, formatter))


class BlogStreamBlock(StreamBlock):
    h2 = CharBlock(icon="title", classname="title")
    h3 = CharBlock(icon="title", classname="title")
    h4 = CharBlock(icon="title", classname="title")
    paragraph = RichTextBlock(icon="pilcrow")
    image = ImageChooserBlock()
    pullquote = PullQuoteBlock()
    document = DocumentChooserBlock(icon="doc-full-inverse")
    code = CodeBlock()


class HomePage(Page):
    description = models.TextField(max_length=400, default='')

    content_panels = Page.content_panels + [
        FieldPanel('description', classname="full"),
    ]


class BlogIndexPage(Page):
    @property
    def blogs(self):
        # Get list of live blog pages that are descendants of this page ordered by most recent
        blogs = BlogPage.objects.live().descendant_of(self).order_by('-date')

        return blogs

    def get_context(self, request):
        # Get blogs
        blogs = self.blogs

        # Filter by tag
        tag = request.GET.get('tag')
        if tag:
            blogs = blogs.filter(tags__name=tag)

        # Filter by date
        filter_date = request.GET.get('date')
        if filter_date:
            filter_date = datetime.strptime(filter_date, '%Y-%m')
            blogs = blogs.filter(date__month=filter_date.month, date__year=filter_date.year)

        # Pagination
        paginator = Paginator(blogs, 10)  # Show 10 blogs per page
        try:
            blogs = paginator.page(request.GET.get('page'))
        except PageNotAnInteger:
            blogs = paginator.page(1)
        except EmptyPage:
            blogs = paginator.page(paginator.num_pages)

        # Update template context
        context = super(BlogIndexPage, self).get_context(request)
        context['blogs'] = blogs
        context['paginator'] = paginator
        return context


class BlogPageTag(TaggedItemBase):
    content_object = ParentalKey('blog.BlogPage', related_name='tagged_items')


class BlogPage(Page):
    body = StreamField(BlogStreamBlock())
    intro = RichTextField(help_text="This is displayed on the home and blog listing pages")
    tags = ClusterTaggableManager(through=BlogPageTag, blank=True)
    date = models.DateField("Post date")

    @property
    def blog_index(self):
        # Find closest ancestor which is a blog index
        return self.get_ancestors().type(BlogIndexPage).last()

    def get_context(self, request):
        context = super(BlogPage, self).get_context(request)
        context['body'] = self.body
        return context


BlogPage.content_panels = [
    FieldPanel('title', classname="full title"),
    FieldPanel('date'),
    FieldPanel('intro'),
    StreamFieldPanel('body'),
]

BlogPage.promote_panels = Page.promote_panels + [
    FieldPanel('tags'),
]


# TODO: Events
class EventsIndexPage(Page):
    pass


# Django doesn't serialise lambdas for makemigrations
def _get_default_end():
    return datetime.now() + timedelta(hours=1)


class EventPage(Page):
    # Event fields
    body = StreamField(BlogStreamBlock())
    description = models.CharField(max_length=200)
    category = models.OneToOneField(EventType, on_delete=models.PROTECT)
    location = models.CharField(max_length=50, default='Department of Computer Science')
    start = models.DateTimeField(default=datetime.now)
    finish = models.DateTimeField(default=_get_default_end())
    cancelled = models.BooleanField()
    facebook_link = models.URLField(verbose_name='Facebook event',
                                    help_text='A link to the associated Facebook event if one exists', blank=True)
    # Event signup fields
    signup_limit = models.IntegerField(verbose_name='Signup limit', help_text='Enter 0 for unlimited signups')
    signup_open = models.DateTimeField()
    signup_close = models.DateTimeField()
    signup_freshers_open = models.DateTimeField(
        help_text='Set a date for when freshers may sign up to the event, leave blank if they are to sign up at the\
                   same time as everyone else', blank=True)
    # TODO: Seating plan association goes here


EventPage.content_panels = [
    MultiFieldPanel([
        FieldPanel('title', classname="full title"),
        FieldPanel('cancelled'),
        FieldPanel('description'),
        FieldPanel('category'),
        FieldPanel('location'),
        FieldPanel('facebook_link'),
        FieldPanel('start'),
        FieldPanel('finish'),
        StreamFieldPanel('body'),
    ], heading='Event details'),
    MultiFieldPanel([
        FieldPanel('signup_limit'),
        FieldPanel('signup_open'),
        FieldPanel('signup_close'),
        FieldPanel('signup_freshers_open')
    ], heading='Signup information')
]


class AboutPage(Page):
    body = StreamField(BlogStreamBlock())
    full_title = models.CharField(max_length=255)

    def get_context(self, request):
        context = super(AboutPage, self).get_context(request)
        context['body'] = self.body
        return context


AboutPage.content_panels = [
    FieldPanel('title', classname="full title"),
    FieldPanel('full_title'),
    StreamFieldPanel('body'),
]


# TODO: Also remove these - Django's migrator is an idiot >.<
class ContactIndexPage(Page):
    pass


class ExecPage(Page):
    pass
