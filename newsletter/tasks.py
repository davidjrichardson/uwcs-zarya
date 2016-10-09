from celery.decorators import task

from django.urls import reverse
from django.core.mail import send_mail

from markdown import markdown

from .models import Subscription, Mail

from bs4 import BeautifulSoup


def mail_newsletter(subscription, mail):
    # Create the unsubscribe link -- there should probably be a better way of doing this
    unsub_link = 'https://uwcs.co.uk{path}'.format(path=reverse('unsub_with_id', kwargs={'email_id': subscription.id}))
    markdown_append = '\n\n[Click here to unsubscribe from the UWCS newsletter]({link})'.format(link=unsub_link)
    text_append = '\n\nClick the following link to unsubscribe from the UWCS newsletter:\n{link}'.format(
        link=unsub_link)

    # Create the plaintext and HTML messages with the appended unsubscribe links
    email_html = markdown(mail.text + markdown_append)

    # Alter image sources to point to the right place
    soup = BeautifulSoup(email_html, 'html5lib')
    for img in soup.findAll('img'):
        img['src'] = 'https://uwcs.co.uk{path}'.format(path=img['src'])
    email_html = str(soup)

    email_text = ''.join(BeautifulSoup(markdown(mail.text), 'html5lib').findAll(text=True)) + text_append
    sender = '{name} <{email}>'.format(name=mail.sender_name, email=mail.sender_email)

    send_mail(subject=mail.subject, from_email=sender, recipient_list=[subscription.email], message=email_text,
              html_message=email_html)


@task(name='send_newsletter')
def send_newsletter(mail_id):
    # Send an individual email to each user, allowing them to unsubscribe
    for subscription in Subscription.objects.all():
        mail_newsletter(subscription, Mail.objects.get(id=mail_id))
