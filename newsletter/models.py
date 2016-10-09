from django.db import models
from django.utils import timezone

from django.utils.datetime_safe import strftime

from markdownx.models import MarkdownxField


class Subscription(models.Model):
    email = models.EmailField()
    date_subscribed = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.email


class Mail(models.Model):
    subject = models.CharField(max_length=120)
    sender_name = models.CharField(max_length=50, default='UWCS Newsletter')
    sender_email = models.EmailField(default='noreply@uwcs.co.uk')
    text = MarkdownxField()
    date_created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return '{subject} - {date}'.format(date=strftime(self.date_created, '%Y-%m-%d'), subject=self.subject)
