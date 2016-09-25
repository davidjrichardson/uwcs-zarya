from celery.decorators import task
from celery.utils.log import get_task_logger

from django.contrib.auth import get_user_model

from accounts.models import ShellAccount

logger = get_task_logger('zarya')


@task(name='create_ldap_user')
def create_ldap_user(account_id):
    request = ShellAccount.objects.get(id=account_id)

    # TODO: Query LDAP for username, fail if username taken and send email
    # TODO: If username free, use student ID as user/group ID and add user with random password
    # TODO: Send email with new credentials to user if success

    return True
