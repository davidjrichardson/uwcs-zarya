from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.template.defaultfilters import slugify, linebreaks

from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.rich_text import RichText

from migration.models import WebsiteDetails, NicknameDetails, OldShellAccount, OldDatabaseAccount, Communication
from accounts.models import CompsocUser, ShellAccount, DatabaseAccount
from blog.models import BlogPage

import time

COMMS_DICT = {
    'NL': 'Newsletter',
    'M': 'Meeting Minutes',
    'N': 'News Item'
}


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


def migrate_old_posts():
    """
    Converts all old posts from a simple page format to one Wagtail accepts
    """
    # id=4 is the specific page ID for the news index page
    index = Page.objects.get(id=4).specific
    old_posts = Communication.objects.using('old_data').all().order_by('date')
    user = get_user_model().objects.get(id=1)

    for post in old_posts:
        if post.title:
            slug = slugify('old news {title} - {rand}'.format(title=post.title, rand=int(round(time.time() * 1000))))
            title = post.title
        else:
            slug = slugify('old news from {date} - rand'.format(date=post.date, rand=int(round(time.time() * 1000))))
            title = 'Old news from {date}'.format(date=post.date)

        page = BlogPage(
            search_description='',
            seo_title=title,
            show_in_menus=False,
            slug=slug,
            title=title,
            date=post.date,
            first_published_at=post.date,
            intro='Archived post from {date}'.format(date=post.date),
        )

        page.body.stream_data = [
            ('paragraph', RichText('<p>{body}</p>'.format(body=linebreaks(post.text))))
        ]

        page.tags.add(COMMS_DICT[post.type])

        index.add_child(instance=page)
        revision = page.save_revision(
            user=user,
            submitted_for_moderation=False
        )
        revision.publish()
        page.save()


class Command(BaseCommand):
    def handle(self, *args, **options):
        migrate_compsoc_memberinfo()
        migrate_old_posts()
