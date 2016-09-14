from django.forms import ModelForm
from .models import CompsocUser, DatabaseAccount, ShellAccount


class CompsocUserForm(ModelForm):
    class Meta:
        model = CompsocUser
        fields = ['nickname', 'website_title', 'website_url']


class ShellAccountForm(ModelForm):
    class Meta:
        model = ShellAccount
        fields = ['name']
        error_messages = {
            'name': {

            }
        }


class DatabaseAccountForm(ModelForm):
    class Meta:
        model = DatabaseAccount
        fields = ['name']
