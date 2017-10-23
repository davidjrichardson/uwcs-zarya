import gc
from celery.decorators import task
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse

from blog.models import Sponsor
from .models import Subscription, Mail


def mail_newsletter(recipients, mail):
    email_context = {
        'title': mail.subject,
        'message': mail.text,
        'base_url': settings.EMAIL_ABS_URL,
        'sponsors': Sponsor.objects.all(),
    }
    email_html = render_to_string('newsletter/email_newsletter.html', email_context)
    email_plaintext = render_to_string('newsletter/email_newsletter.txt', email_context)
    to = [x.email for x in recipients]
    # Create a map of emails to unsub tokens for the email merge
    unsub_tokens = {recipient.email: {
        'unsub_url': '{hostname}{path}'.format(hostname=settings.EMAIL_ABS_URL,
                                               path=reverse('unsub_with_id', kwargs={
                                                   'token': recipient.unsubscribe_token
                                               }))} for recipient in recipients}
    sender = '{name} <{email}>'.format(name=mail.sender_name, email=mail.sender_email)

    email = EmailMultiAlternatives(mail.subject, email_plaintext, sender, to)
    email.attach_alternative(email_html, 'text/html')
    email.merge_data = unsub_tokens
    email.send()


def queryset_iterator(queryset, chunk_size=1000):
    """
    Iterate over a Django Queryset ordered by the primary key
    This method loads a maximum of chunk_size (default: 1000) rows in it's
    memory at the same time while django normally would load all rows in it's
    memory. Using the iterator() method only causes it to not preload all the
    classes.
    Note that the implementation of the iterator does not support ordered query sets.
    """
    try:
        last_pk = queryset.order_by('-pk')[:1].get().pk
    except ObjectDoesNotExist:
        return

    pk = 0
    queryset = queryset.order_by('pk')
    while pk < last_pk:
        for row in queryset.filter(pk__gt=pk)[:chunk_size]:
            pk = row.pk
            yield row
        gc.collect()


@task(name='send_newsletter')
def send_newsletter(mail_id):
    subscriptions = queryset_iterator(Subscription.objects.all(), chunk_size=500)

    for chunk in subscriptions:
        mail_newsletter(chunk, Mail.objects.get(id=mail_id))
