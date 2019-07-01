import re
from datetime import date

from django.conf import settings
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models
from django.db.models.signals import post_save

username_pattern = re.compile(r'^[a-z0-9]+$')

STATUS = (
    ('RE', 'Requested'),
    ('PR', 'Enabled'),
    ('DD', 'Disabled'),
)


class CompsocUser(models.Model):
    nickname = models.CharField(max_length=50, blank=True, default='')
    first_name = models.CharField(max_length=50, blank=True, default='')
    last_name = models.CharField(max_length=50, blank=True, default='')

    discord_user = models.CharField(max_length=50, blank=True, default='')

    nightmode_on = models.BooleanField(default=False,
                                       help_text='Enable night mode whenever you are logged into UWCS - overrides the nightmode switch in the footer')

    website_url = models.CharField(max_length=50, blank=True, default='')
    website_title = models.CharField(max_length=50, blank=True, default='')

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    @property
    def abs_website_url(self):
        if self.website_url.startswith(('http://', 'https://')):
            return self.website_url
        else:
            return 'http://{url}'.format(url=self.website_url)

    def __str__(self):
        return self.name()

    def is_fresher(self):
        return self.user.username.startswith(str(date.today().year)[2:])

    def name(self):
        if self.nickname.strip():
            return self.nickname.strip()
        else:
            return self.full_name()

    def full_name(self):
        if self.first_name:
            return '{} {}'.format(self.first_name.strip(), self.last_name.strip())
        else:
            return self.user.get_full_name()

    def long_name(self):
        if self.nickname.strip():
            return self.nickname.strip()
        else:
            return self.full_name()


# Create a CompsocUser object for every new user
def ensure_compsocuser_callback(sender, instance, **kwargs):
    profile, new = CompsocUser.objects.get_or_create(user=instance)


post_save.connect(ensure_compsocuser_callback, sender=User)


class ShellAccount(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=30,
                            error_messages={'regex': 'The name must contain all lowercase alphanumeric characters'},
                            validators=[RegexValidator(regex=username_pattern, code='regex')])
    status = models.CharField(max_length=2, choices=STATUS)

    def __str__(self):
        return self.name


class DatabaseAccount(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=30,
                            error_messages={'regex': 'The name must contain all lowercase alphanumeric characters'},
                            validators=[RegexValidator(regex=username_pattern, code='regex')])
    status = models.CharField(max_length=2, choices=STATUS)

    def __str__(self):
        return self.name


class ExecPosition(models.Model):
    title = models.CharField(max_length=30)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title


class ExecPlacement(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    position = models.ForeignKey(ExecPosition, on_delete=models.CASCADE)
    start = models.DateField()
    end = models.DateField()

    class Meta:
        ordering = ['start']

    def __str__(self):
        return "{start}/{end} - {pos}".format(start=self.start.year, end=self.end.year,
                                              pos=self.position)
