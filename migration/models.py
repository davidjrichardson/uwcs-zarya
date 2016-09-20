from django.contrib.auth.models import User
from django.db import models
from datetime import datetime, timedelta

TARGETS = (
    ('ACA', 'Academic'),
    ('GAM', 'Gaming'),
    ('SCL', 'Social'),
    ('SCT', 'Society'),
)


class EventType(models.Model):
    name = models.CharField(max_length=20)
    info = models.TextField()
    target = models.CharField(max_length=3, choices=TARGETS)

    class Meta:
        app_label = 'events'


class Event(models.Model):
    """
    Represents a single event
    """
    # I'm never using camel case for model fields again :p
    type = models.ForeignKey(EventType)
    shortDescription = models.CharField(max_length=255, verbose_name="Short Description",
                                        help_text="This text is displayed on the events index.")
    longDescription = models.TextField(verbose_name="Long Description",
                                       help_text="This text is displayed on the details page for this event.")
    start = models.DateTimeField(default=datetime.now)
    finish = models.DateTimeField(default=lambda: datetime.now() + timedelta(hours=1))
    displayFrom = models.DateTimeField(default=datetime.now, verbose_name="Display From",
                                       help_text="This controls when the event will be visible in the index and feeds.")
    cancelled = models.BooleanField()

    class Meta:
        app_label = 'events'


class EventSignup(models.Model):
    """
    This represents the signup options for a particular event,
    e.g Signup limits and time constraints
    This might be renamed to EventSignupOptions
    """
    event = models.OneToOneField(Event)
    signupsLimit = models.IntegerField(verbose_name="Signups Limit", help_text="0 here implies unlimited signups.")
    open = models.DateTimeField()
    close = models.DateTimeField()
    fresher_open = models.DateTimeField(
        help_text="This allows you to control whether freshers can sign up earlier or later than regular members.")
    guest_open = models.DateTimeField(
        help_text="This allows you to control whether guests can sign up earlier or later than regular members.")

    # this might be renamed to seating_plan for clarity

    class Meta:
        app_label = 'events'


class Signup(models.Model):
    event = models.ForeignKey(Event)
    time = models.DateTimeField()
    user = models.ForeignKey(User)
    comment = models.TextField(blank=True)

    class Meta:
        app_label = 'events'
