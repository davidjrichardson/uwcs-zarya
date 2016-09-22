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


class Command(BaseCommand):
    def handle(self, *args, **options):
        members_xml = requests.get('{prefix}{key}/'.format(prefix=API_PREFIX,
                                                           key=settings.UNION_API_KEY))
        members_root = fromstring(members_xml.text.encode('utf-8'))
        active_members = []

        # Add any new members
        for member in members_root:
            try:
                current_member = User.objects.get(username=member.find('UniqueID').text)
                if current_member.is_active:
                    active_members.append(current_member.id)
            except User.DoesNotExist:
                password = User.objects.make_random_password()
                new_user = User.objects.create_user(username=member.find('UniqueID').text,
                                                    email=member.find('EmailAddress').text,
                                                    password=password)
                # TODO: Email the password to the user
                new_user.first_name = title(member.find('FirstName').text.encode('utf-8'))
                new_user.last_name = title(member.find('LastName').text.encode('utf-8'))
                new_user.save()

                active_members.append(new_user)

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
