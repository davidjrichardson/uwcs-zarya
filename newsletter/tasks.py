from celery.decorators import task
from django.conf import settings
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


@task(name='send_newsletter')
def send_newsletter(mail_id):
    mail_newsletter(Subscription.objects.all(), Mail.objects.get(id=mail_id))
