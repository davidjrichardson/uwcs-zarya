from datetime import timedelta, datetime
from collections import OrderedDict

from taggit.models import TaggedItemBase

from wagtail.wagtailadmin.edit_handlers import FieldPanel, StreamFieldPanel, MultiFieldPanel
from wagtail.wagtailcore.fields import StreamField
from wagtail.wagtailcore.models import Page

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.paginator import PageNotAnInteger, Paginator, EmptyPage

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


class EventsIndexPage(Page):
    # Parent page/subpage rules
    parent_page_types = ['blog.HomePage']
    subpage_types = ['events.EventPage', 'events.EventsArchivePage']

    @property
    def events(self):
        events = EventPage.objects.live().descendant_of(self).filter(finish__gte=timezone.now()).order_by('start')

        return events

    def get_context(self, request, *args, **kwargs):
        context = super(EventsIndexPage, self).get_context(request)

        events = self.events
        weeks_dict = OrderedDict()

        for event in events:
            event_week = event.start.isocalendar()[1]
            key = '{year}-{week}'.format(year=event.start.year, week=event_week)

            if weeks_dict.get(key):
                weeks_dict.get(key).append(event)
            else:
                weeks_dict[key] = [event]

        weeks = list()

        for _, week in weeks_dict.items():
            weeks.append(week)

        context['weeks'] = weeks

        return context


class EventsArchivePage(Page):
    # Parent page/subpage rules
    parent_page_types = ['events.EventsIndexPage']

    @property
    def archive_events(self):
        events = EventPage.objects.live().descendant_of(self.get_parent()).filter(finish__lt=timezone.now()).order_by(
            '-start')

        return events

    def get_context(self, request, *args, **kwargs):
        context = super(EventsArchivePage, self).get_context(request)

        events = self.archive_events

        # Filter by date
        filter_date = request.GET.get('date')
        if filter_date:
            filter_date = datetime.strptime(filter_date, '%Y-%m')
            events = events.filter(start__month=filter_date.month, start__year=filter_date.year)

        weeks_dict = OrderedDict()

        for event in events:
            event_week = event.start.isocalendar()[1]
            key = '{year}-{week}'.format(year=event.start.year, week=event_week)

            if weeks_dict.get(key):
                weeks_dict.get(key).append(event)
            else:
                weeks_dict[key] = [event]

        weeks = list()

        for _, week in weeks_dict.items():
            weeks.append(week)

        # Pagination
        paginator = Paginator(weeks, 8)  # Show 8 weeks per page
        try:
            weeks = paginator.page(request.GET.get('page'))
        except PageNotAnInteger:
            weeks = paginator.page(1)
        except EmptyPage:
            weeks = paginator.page(paginator.num_pages)

        context['weeks'] = weeks
        context['paginator'] = paginator

        return context


class EventPage(Page):
    # Parent page/subpage rules
    parent_page_types = ['events.EventsIndexPage']

    # Event fields
    body = StreamField(BlogStreamBlock())
    description = models.TextField()
    category = models.ForeignKey(EventType, on_delete=models.PROTECT)
    location = models.CharField(max_length=50, default='Department of Computer Science')
    start = models.DateTimeField(default=timezone.now)
    finish = models.DateTimeField(default=timezone.now)
    cancelled = models.BooleanField()
    facebook_link = models.URLField(verbose_name='Facebook event',
                                    help_text='A link to the associated Facebook event if one exists', blank=True,
                                    default='')
    # Event signup fields
    signup_limit = models.IntegerField(verbose_name='Signup limit',
                                       help_text='Enter 0 for unlimited signups or -1 for no signups',
                                       default=-1)
    signup_open = models.DateTimeField(default=timezone.now)
    signup_close = models.DateTimeField(default=timezone.now)
    signup_freshers_open = models.DateTimeField(
        help_text='Set a date for when freshers may sign up to the event, leave blank if they are to sign up at the\
                   same time as everyone else', blank=True, null=True)

    # TODO: Seating plan association goes here

    @property
    def is_ongoing(self):
        if self.start < timezone.now() <= self.finish:
            return True
        else:
            return False

    @property
    def signups(self):
        signups = EventSignup.objects.filter(event=self).all().order_by('-signup_created')

        return signups

    def get_context(self, request, *args, **kwargs):
        context = super(EventPage, self).get_context(request)

        if request.user.is_authenticated() and self.signups.filter(member=request.user).exists():
            user_signed_up = True
        else:
            user_signed_up = False

        context['user_signed_up'] = user_signed_up

        if request.user.is_authenticated():
            try:
                user = CompsocUser.objects.get(user=request.user.id)

                if user.is_fresher() and self.signup_freshers_open:
                    in_signup_window = self.signup_freshers_open < timezone.now() <= self.signup_close
                else:
                    in_signup_window = self.signup_open < timezone.now() <= self.signup_close
            except CompsocUser.DoesNotExist:
                in_signup_window = self.signup_open < timezone.now() <= self.signup_close
        else:
            in_signup_window = False

        if self.signup_limit == -1:
            context['can_signup'] = False
        elif self.signup_limit == 0:
            context['can_signup'] = in_signup_window
        elif self.signups.count() < self.signup_limit:
            context['can_signup'] = in_signup_window
        else:
            context['can_signup'] = False

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
    comment = models.CharField(blank=True, max_length=1024)

    def __str__(self):
        try:
            return self.member.compsocuser.full_name()
        except CompsocUser.DoesNotExist:
            return self.member.get_full_name()

    class Meta:
        ordering = ['signup_created']
        unique_together = ('event', 'member')
