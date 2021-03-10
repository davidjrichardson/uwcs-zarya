from django.core.management.base import BaseCommand
from django.conf import settings

from django.template.defaultfilters import title

from django.contrib.auth.models import User

import requests

# Use the C ElementTree implementation where possible
try:
    from xml.etree.cElementTree import ElementTree, fromstring
except ImportError:
    from xml.etree.ElementTree import ElementTree, fromstring

API_PREFIX = 'https://www.warwicksu.com/membershipapi/listMembers/'


def send_signup_mail(user, password):
    subject = 'Welcome to the University of Warwick Computing Society'
    from_email = 'UWCS Exec <noreply@uwcs.co.uk>'
    message = 'Thanks for joining the society! Your login details are as follows:\n\n' \
              'Username: {username}\n' \
              'Password: {password}\n\n' \
              'You can log in at https://uwcs.co.uk/accounts/login/. We suggest you change your \n' \
              'password as soon as you log in. Don\'t forget to add a nickname, too!\n\n' \
              'Regards,\n' \
              'UWCS Exec\n\n' \
              'P.S.: Please don\'t reply to this email, you will not get a response.'.format(username=user.username, 
                                                                                             password=password)
    user.email_user(subject, message, from_email)


class Command(BaseCommand):
    def handle(self, *args, **options):
        members_xml = requests.get('{prefix}{key}/'.format(prefix=API_PREFIX,
                                                           key=settings.UNION_API_KEY))
        members_root = fromstring(members_xml.text.encode('utf-8'))
        active_members = []

        # Add any new members
        for member in members_root:
            try:
                if member.find('UniqueID').text:
                    current_member = User.objects.get(username=member.find('UniqueID').text)
                    active_members.append(current_member.id)
            except User.DoesNotExist:
                # Create the user and then email their password to them
                password = User.objects.make_random_password()
                new_user = User.objects.create_user(username=member.find('UniqueID').text,
                                                    email=member.find('EmailAddress').text,
                                                    password=password)
                new_user.first_name = title(member.find('FirstName').text)
                new_user.last_name = title(member.find('LastName').text)
                new_user.save()
                send_signup_mail(new_user, password)
                active_members.append(new_user.id)

        # Handle special cases with Ex-exec, exec and staff/superuser status
        for member in User.objects.all():
            if member.groups.filter(name__in=['Ex-exec', 'Exec']).exists():
                if member not in active_members:
                    active_members.append(member.id)
            elif member.is_staff or member.is_superuser:
                if member not in active_members:
                    active_members.append(member.id)

        # Ensure all accounts that are to be activate are so
        activated = User.objects.filter(id__in=active_members).all()
        activated.update(is_active=True)

        # Deactivate old accounts
        deactivated = User.objects.exclude(id__in=active_members).all()
        deactivated.update(is_active=False)
