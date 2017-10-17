import crypt
import os
import subprocess
from datetime import datetime

from celery.decorators import task
from django.conf import settings
from django.contrib.auth.models import User
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
    html_template = get_template('accounts/usersite_template.html')
    html = html_template.render({
        'nickname': username
    })

    # Write the file to disk
    index_path = '{website_dir}/{nickname}/index.html'.format(website_dir=settings.APACHE_WEBSITE_DIR, nickname=username)
    index_file = open(index_path, 'w')
    index_file.write(html)
    index_file.close()

    # Change ownership and set permissions of the file
    os.chown(index_path, uid, uid)
    # 0o644 is the same as 644 permissions.
    os.chmod(index_path, 0o644)


def send_user_issue_email(user, username):
    subject = 'There\'s an issue with your shell account request'
    from_email = 'UWCS Techteam <noreply@uwcs.co.uk>'
    message = 'Hi {first_name},\n\n' \
              'Unfortunately the nickname that you had provided for your shell account ({username}) is in use \n' \
              'which means we can\'t create an account for you. No worries though, just send an email \n' \
              'to tech@uwcs.co.uk explaining the situation the account name that you\'d like and we \n' \
              'should be able to sort things out for you.\n\n' \
              'Regards,\n' \
              'UWCS Tech Team\n\n' \
              'P.S.: Please don\'t reply to this email, you will not get a response.'.format(first_name=user.first_name,
                                                                                             username=username)
    user.email_user(subject, message, from_email)


def send_success_mail(user, username, password):
    subject = 'Shell account request successful'
    from_email = 'UWCS Techteam <noreply@uwcs.co.uk>'
    message = 'Your shell account request has been successful and an account has been created with the \n' \
              'following credentials:\n\n' \
              'username: {username}\n' \
              'password: {password}\n\n' \
              'You can access our server(s) by using ssh and the address lovelace.uwcs.co.uk. We recommend you ' \
              'change your password using the passwd command once logged in. From \'lovelace\', you then may ' \
              'log into our other servers. A full breakdown of our servers and what they \n' \
              'do is available on our about page: https://uwcs.co.uk/about/\n\n' \
              'Regards,\n' \
              'UWCS Tech Team\n\n' \
              'P.S.: Please don\'t reply to this email, you will not get a response.'.format(username=username,
                                                                                             password=password)
    user.email_user(subject, message, from_email)


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
