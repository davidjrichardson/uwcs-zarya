from datetime import datetime

from django import forms
from django.core.paginator import PageNotAnInteger, Paginator, EmptyPage
from django.db import models
from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase
from wagtail.wagtailadmin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.wagtailcore.blocks import TextBlock, StructBlock, StreamBlock, FieldBlock, CharBlock, RichTextBlock, \
    RawHTMLBlock
from wagtail.wagtailcore.fields import StreamField
from wagtail.wagtailcore.models import Page
from wagtail.wagtaildocs.blocks import DocumentChooserBlock
from wagtail.wagtailimages.blocks import ImageChooserBlock
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailsnippets.models import register_snippet


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


class PullQuoteBlock(StructBlock):
    quote = TextBlock("quote title")
    attribution = CharBlock()

    class Meta:
        icon = "openquote"


class ImageFormatChoiceBlock(FieldBlock):
    field = forms.ChoiceField(choices=(
        ('left', 'Wrap left'), ('right', 'Wrap right'), ('mid', 'Mid width'), ('full', 'Full width'),
    ))


class HTMLAlignmentChoiceBlock(FieldBlock):
    field = forms.ChoiceField(choices=(
        ('normal', 'Normal'), ('full', 'Full width'),
    ))


class ImageBlock(StructBlock):
    image = ImageChooserBlock()
    caption = RichTextBlock()
    alignment = ImageFormatChoiceBlock()


class AlignedHTMLBlock(StructBlock):
    html = RawHTMLBlock()
    alignment = HTMLAlignmentChoiceBlock()

    class Meta:
        icon = "code"


class BlogStreamBlock(StreamBlock):
    h2 = CharBlock(icon="title", classname="title")
    h3 = CharBlock(icon="title", classname="title")
    h4 = CharBlock(icon="title", classname="title")
    intro = RichTextBlock(icon="pilcrow")
    paragraph = RichTextBlock(icon="pilcrow")
    aligned_image = ImageBlock(label="Aligned image", icon="image")
    pullquote = PullQuoteBlock()
    aligned_html = AlignedHTMLBlock(icon="code", label='Raw HTML')
    document = DocumentChooserBlock(icon="doc-full-inverse")


class HomePage(Page):
    description = models.TextField(max_length=400, default='')

    content_panels = Page.content_panels + [
        FieldPanel('description', classname="full"),
    ]


class BlogIndexPage(Page):
    @property
    def blogs(self):
        # Get list of live blog pages that are descendants of this page
        blogs = BlogPage.objects.live().descendant_of(self)

        # Order by most recent date first
        blogs = blogs.order_by('-date')

        return blogs

    @property
    def archives(self):
        archives = dict()
        for blog in self.blogs:
            archives.setdefault(blog.date.year, {}).setdefault(blog.date.month, []).append(blog)

        return archives

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

        print(paginator.num_pages)

        # Update template context
        context = super(BlogIndexPage, self).get_context(request)
        context['blogs'] = blogs
        context['paginator'] = paginator
        context['archives'] = self.archives
        return context


class BlogPageTag(TaggedItemBase):
    content_object = ParentalKey('blog.BlogPage', related_name='tagged_items')


class BlogPage(Page):
    body = StreamField(BlogStreamBlock())
    tags = ClusterTaggableManager(through=BlogPageTag, blank=True)
    date = models.DateField("Post date")
    feed_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    @property
    def blog_index(self):
        # Find closest ancestor which is a blog index
        return self.get_ancestors().type(BlogIndexPage).last()

BlogPage.content_panels = [
    FieldPanel('title', classname="full title"),
    FieldPanel('date'),
    StreamFieldPanel('body'),
]

BlogPage.promote_panels = Page.promote_panels + [
    ImageChooserPanel('feed_image'),
    FieldPanel('tags'),
]
