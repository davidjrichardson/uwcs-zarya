from collections import defaultdict

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model

from migration.models import WebsiteDetails, NicknameDetails, OldShellAccount, OldDatabaseAccount
from accounts.models import CompsocUser, ShellAccount, DatabaseAccount


def migrate_compsoc_memberinfo():
    """
    Amalgamates the old user detail objects into the new CompsocUser and other models
    """
    websites = WebsiteDetails.objects.using('old_data').all()
    nicks = NicknameDetails.objects.using('old_data').all()
    shell_accounts = OldShellAccount.objects.using('old_data').all()
    db_accounts = OldDatabaseAccount.objects.using('old_data').all()
    userinfo = {}

    # Handle shell accounts
    for account in shell_accounts:
        user = get_user_model().objects.filter(id=account.user_id).first()
        new_account = ShellAccount(name=account.name, user=user, status=account.status)
        new_account.save()

    # Handle DB accounts
    for account in db_accounts:
        user = get_user_model().objects.filter(id=account.user_id).first()
        new_account = DatabaseAccount(name=account.name, user=user, status=account.status)
        new_account.save()

    # Handle transfer of Nickname info to CompsocUser model
    for nick in nicks:
        user_id = nick.user_id

        userinfo[user_id] = {
            'nickname': nick.nickname,
            'website_title': '',
            'website_url': ''
        }

    # Handle transfer of Website info to CompsocUser model
    for site in websites:
        user_id = site.user_id

        if user_id in userinfo:
            userinfo[user_id]['website_title'] = site.websiteTitle
            userinfo[user_id]['website_url'] = site.websiteUrl
        else:
            userinfo[user_id] = {
                'nickname': '',
                'website_title': site.websiteTitle,
                'website_url': site.websiteUrl
            }

    # Save new CompsocUser info
    for uid, details in userinfo.items():
        user = get_user_model().objects.filter(id=uid).first()
        new_userinfo = CompsocUser(nickname=details['nickname'], website_title=details['website_title'],
                               website_url=details['website_url'], user=user)

        new_userinfo.save()


class Command(BaseCommand):
    def handle(self, *args, **options):
        migrate_compsoc_memberinfo()
