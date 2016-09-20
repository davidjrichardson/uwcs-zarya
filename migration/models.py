from django.contrib.auth.models import User
from django.db import models
from datetime import datetime, timedelta

TARGETS = (
    ('ACA', 'Academic'),
    ('GAM', 'Gaming'),
    ('SCL', 'Social'),
    ('SCT', 'Society'),
)

COMMS_TYPE = (
    ('NL', 'Newsletter'),
    ('M', 'Minute'),
    ('N', 'News Item'),
)

STATUS = (
    ('RE', 'Requested'),
    ('PR', 'Present'),
    ('DD', 'Disabled'),
)


# The following models are copied from the previous compsoc website (Django Reinhardt)

class Communication(models.Model):
    title = models.CharField(max_length=100)
    date = models.DateField()
    text = models.TextField()
    type = models.CharField(max_length=2, choices=COMMS_TYPE)


class OldEventType(models.Model):
    name = models.CharField(max_length=20)
    info = models.TextField()
    target = models.CharField(max_length=3, choices=TARGETS)

    class Meta:
        db_table = 'events_eventtype'


class OldEvent(models.Model):
    """
    Represents a single event
    """
    # I'm never using camel case for model fields again :p
    type = models.ForeignKey(OldEventType)
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
        db_table = 'events_event'


class OldEventSignup(models.Model):
    """
    This represents the signup options for a particular event,
    e.g Signup limits and time constraints
    This might be renamed to EventSignupOptions
    """
    event = models.OneToOneField(OldEvent)
    signupsLimit = models.IntegerField(verbose_name="Signups Limit", help_text="0 here implies unlimited signups.")
    open = models.DateTimeField()
    close = models.DateTimeField()
    fresher_open = models.DateTimeField(
        help_text="This allows you to control whether freshers can sign up earlier or later than regular members.")
    guest_open = models.DateTimeField(
        help_text="This allows you to control whether guests can sign up earlier or later than regular members.")

    # this might be renamed to seating_plan for clarity

    class Meta:
        db_table = 'events_eventsignup'


class Signup(models.Model):
    event = models.ForeignKey(OldEvent)
    time = models.DateTimeField()
    user = models.ForeignKey(User)
    comment = models.TextField(blank=True)

    class Meta:
        db_table = 'events_signup'


class Member(models.Model):
    """
    Used to store auxiliary data to the default profile data for
    a django User.
    """
    user = models.OneToOneField(User)
    showDetails = models.BooleanField()
    guest = models.BooleanField()


# Optional info about one's website
class WebsiteDetails(models.Model):
    user = models.OneToOneField(User)
    websiteUrl = models.CharField(max_length=50)
    websiteTitle = models.CharField(max_length=50)

    class Meta:
        db_table = 'memberinfo_websitedetails'


class NicknameDetails(models.Model):
    user = models.OneToOneField(User)
    nickname = models.CharField(max_length=20)

    class Meta:
        db_table = 'memberinfo_nicknamedetails'


class OldShellAccount(models.Model):
    user = models.OneToOneField(User)
    name = models.CharField(max_length=30)
    status = models.CharField(max_length=2, choices=STATUS)

    class Meta:
        db_table = 'memberinfo_shellaccount'


class OldDatabaseAccount(models.Model):
    user = models.OneToOneField(User)
    name = models.CharField(max_length=30)
    status = models.CharField(max_length=2, choices=STATUS)

    class Meta:
        db_table = 'memberinfo_databaseaccount'


class OldExecPosition(models.Model):
    """
    Represents an exec position
    """
    title = models.CharField(max_length=30)

    class Meta:
        db_table = 'memberinfo_execposition'


class OldExecPlacement(models.Model):
    """
    Represents a time period of working on the exec
    """
    position = models.ForeignKey(OldExecPosition)
    user = models.ForeignKey(User)
    start = models.DateField()
    end = models.DateField()

    class Meta:
        db_table = 'memberinfo_execplacement'
