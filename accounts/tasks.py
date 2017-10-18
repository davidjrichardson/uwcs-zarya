import crypt
import os
import subprocess
from datetime import datetime

from celery.decorators import task
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from ldap3 import Connection, Server, SYNC, SIMPLE, ALL_ATTRIBUTES

from accounts.models import ShellAccount


def make_user_site_config(username):
    # Render the config file
    config = render_to_string('accounts/members_template.conf', {
        'user': username,
        'ssl_cipher_suite': settings.APACHE_SSL_CIPHER_SUITE,
        'ssl_cert': settings.APACHE_SSL_CERT_FILE,
        'ssl_key': settings.APACHE_SSL_KEY_FILE,
        'ssl_chain': settings.APACHE_SSL_CHAIN_FILE,
        'website_dir': settings.APACHE_WEBSITE_DIR,
        'base_url': settings.BASE_URL
    })

    # Save it to a file on the filesystem
    config_file = open(
        '{sites_available}/members-{nickname}.conf'.format(sites_available=settings.APACHE_SITES_AVAILABLE,
                                                           nickname=username), 'w')
    config_file.write(config)
    config_file.close()

    # Symlink the config files to enable the site and restart apache
    os.symlink('{sites_available}/members-{nickname}.conf'.format(sites_available=settings.APACHE_SITES_AVAILABLE,
                                                                  nickname=username),
               '{sites_enabled}/members-{nickname}.conf'.format(sites_enabled=settings.APACHE_SITES_ENABLED,
                                                                nickname=username))
    subprocess.call(['service', 'apache2', 'reload'], shell=False)


def make_user_site_placeholder(username, uid):
    # Render the HTML for the new placeholder site
    html = render_to_string('accounts/usersite_template.html', {
        'nickname': username
    })

    # Write the file to disk
    index_path = '{website_dir}/{nickname}/index.html'.format(website_dir=settings.APACHE_WEBSITE_DIR,
                                                              nickname=username)
    index_file = open(index_path, 'w')
    index_file.write(html)
    index_file.close()

    # Change ownership and set permissions of the file
    os.chown(index_path, uid, uid)
    # 0o644 is the same as 644 permissions.
    os.chmod(index_path, 0o644)


def send_user_issue_email(user, username):
    email_context = {
        'title': 'There\'s an issue with your shell account request',
        'first_name': user.first_name,
        'username': username
    }
    email_html = render_to_string('accounts/shell_unsuccessful.html', email_context)
    email_text = render_to_string('accounts/shell_unsuccessful.txt', email_context)

    email = EmailMultiAlternatives(email_context['title'], email_text, 'UWCS Techteam <techteam@uwcs.co.uk>',
                                   to=[user.email])
    email.attach_alternative(email_html, 'text/html')
    email.send()


def send_success_mail(user, username, password):
    email_context = {
        'title': 'Shell account request successful',
        'username': username,
        'password': password,
    }
    email_html = render_to_string('accounts/shell_successful.html', email_context)
    email_text = render_to_string('accounts/shell_successful.txt', email_context)

    email = EmailMultiAlternatives(email_context['title'], email_text, 'UWCS Techteam <techteam@uwcs.co.uk>',
                                   to=[user.email])
    email.attach_alternative(email_html, 'text/html')
    email.send()


@task(name='create_ldap_user')
def create_ldap_user(account_id):
    request = ShellAccount.objects.get(id=account_id)
    user = request.user

    # Setup the LDAP connection
    ldap_server = Server(settings.LDAP_URL, port=settings.LDAP_PORT)
    ldap_conn = Connection(ldap_server, user=settings.LDAP_USER, password=settings.LDAP_PASSWORD,
                           client_strategy=SYNC, authentication=SIMPLE)
    ldap_conn.bind()

    # Search for the user on LDAP
    search_string_user = 'uid={username},ou=People,dc=uwcs,dc=co,dc=uk'.format(username=request.name)
    search_string_group = 'cn={username},ou=Group,dc=uwcs,dc=co,dc=uk'.format(username=request.name)

    ldap_conn.search(search_string_user, '(objectClass=*)', attributes=ALL_ATTRIBUTES)
    user_search = ldap_conn.response

    ldap_conn.search(search_string_group, '(objectClass=*)', attributes=ALL_ATTRIBUTES)
    group_search = ldap_conn.response

    if user_search or group_search:
        # Update request to 'disabled' as representation of the failure
        request.status = 'DD'
        request.save()

        send_user_issue_email(user, request.name)

        return False
    else:
        password = User.objects.make_random_password(length=20)
        salt = crypt.mksalt(crypt.METHOD_SHA512)
        password_hashed = '{crypt}' + crypt.crypt(password, salt)
        days_since_epoch = (datetime.utcnow() - datetime(1970, 1, 1)).days

        group_add_dn = 'cn={nickname},ou=Groups,dc=uwcs,dc=co,dc=uk'.format(nickname=request.name)
        group_attributes_dict = {
            'objectClass': ['posixGroup', 'top'],
            'cn': request.name,
            'gidNumber': [int(user.username)],
            'userPassword': [password_hashed],
        }

        ldap_conn.add(group_add_dn, attributes=group_attributes_dict)

        user_add_dn = 'uid={nickname},ou=People,dc=uwcs,dc=co,dc=uk'.format(nickname=request.name)
        user_attributes_dict = {
            'objectClass': ['account', 'posixAccount', 'top', 'shadowAccount'],
            'cn': [user.get_full_name()],
            'gidNumber': [int(user.username)],
            'uid': [request.name],
            'uidNumber': [int(user.username)],
            'homeDirectory': ['/compsoc/home/{nickname}'.format(nickname=request.name)],
            'loginShell': ['/bin/bash'],
            'shadowWarning': ['7'],
            'shadowLastChange': [days_since_epoch],
            'shadowMax': ['99999'],
            'gecos': ['{fullname}'.format(fullname=user.get_full_name())],
            'userPassword': [password_hashed],
        }

        ldap_conn.add(user_add_dn, attributes=user_attributes_dict)

        request.status = 'PR'
        request.save()

        sites_path = '/compsoc/sites/{nickname}'.format(nickname=request.name)
        if not os.path.exists(sites_path):
            os.makedirs(sites_path)
            os.chown(sites_path, int(user.username), int(user.username))

        apache_conf_path = '{apache}/member-{nickname}.conf'.format(apache=settings.APACHE_SITES_AVAILABLE,
                                                                    nickname=request.name)
        if not os.path.exists(apache_conf_path):
            make_user_site_config(request.name)
            make_user_site_placeholder(username=request.name, uid=int(user.username))

        send_success_mail(user, request.name, password)

        return True
