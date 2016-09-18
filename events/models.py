from datetime import timedelta

from taggit.models import TaggedItemBase

from wagtail.wagtailadmin.edit_handlers import FieldPanel, StreamFieldPanel, MultiFieldPanel
from wagtail.wagtailcore.fields import StreamField
from wagtail.wagtailcore.models import Page

from django.db import models
from django.conf import settings
from django.utils import timezone

from accounts.models import CompsocUser
from blog.models import BlogStreamBlock

TARGETS = (
    ('ACA', 'Academic'),
    ('GAM', 'Gaming'),
    ('SCL', 'Social'),
    ('SCT', 'Society'),
)


class EventType(models.Model):
    name = models.CharField(max_length=50)
    target = models.CharField(max_length=3, choices=TARGETS)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


# Django doesn't serialise lambdas for makemigrations
def _get_default_end():
    return timezone.now() + timedelta(hours=1)


class EventsIndexPage(Page):
    def get_context(self, request, *args, **kwargs):
        context = super(EventsIndexPage, self).get_context(request)
        # TODO: Get upcoming events, split them by week
        return context


class EventPage(Page):
    # Event fields
    body = StreamField(BlogStreamBlock())
    description = models.CharField(max_length=200)
    category = models.OneToOneField(EventType, on_delete=models.PROTECT)
    location = models.CharField(max_length=50, default='Department of Computer Science')
    start = models.DateTimeField(default=timezone.now)
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
                   same time as everyone else', blank=True, null=True)

    # TODO: Seating plan association goes here

    def get_context(self, request, *args, **kwargs):
        context = super(EventPage, self).get_context(request)

        signups = EventSignup.objects.filter(event=self).all()
        context['signups'] = signups
        context['can_signup'] = (self.signup_limit != signups.count())

        if request.user.is_authenticated() and signups.filter(member=request.user).first():
            user_signed_up = True
        else:
            user_signed_up = False

        context['user_signed_up'] = user_signed_up

        return context


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


class EventSignup(models.Model):
    member = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    event = models.ForeignKey(EventPage, on_delete=models.CASCADE)
    signup_created = models.DateTimeField(default=timezone.now)
    comment = models.CharField(blank=True, max_length=140)

    def __str__(self):
        try:
            return self.member.compsocuser.full_name()
        except CompsocUser.DoesNotExist:
            return self.member.get_full_name()

    class Meta:
        ordering = ['signup_created']
        unique_together = ('event', 'member')
