from django.db import models
from django.utils import timezone

from django.utils.datetime_safe import strftime

from hashlib import sha256

from markdownx.models import MarkdownxField


def generate_unsub_token(email, date):
    return sha256('{date}:{email}'.format(date=date, email=email).encode()).hexdigest()


class Subscription(models.Model):
    email = models.EmailField()
    date_subscribed = models.DateTimeField(default=timezone.now)
    unsubscribe_token = models.CharField(max_length=64, blank=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.unsubscribe_token = generate_unsub_token(self.email, self.date_subscribed)

        super(Subscription, self).save(*args, **kwargs)

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
