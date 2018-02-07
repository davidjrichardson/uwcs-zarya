from django.forms import ModelForm
from .models import CompsocUser, DatabaseAccount, ShellAccount


class CompsocUserForm(ModelForm):
    class Meta:
        model = CompsocUser
        fields = ['nickname', 'first_name', 'last_name', 'discord_user', 'nightmode_on', 'website_title', 'website_url']


class ShellAccountForm(ModelForm):
    class Meta:
        model = ShellAccount
        fields = ['name']


class DatabaseAccountForm(ModelForm):
    class Meta:
        model = DatabaseAccount
        fields = ['name']
