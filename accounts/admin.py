from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model

from accounts.models import CompsocUser, ShellAccount, DatabaseAccount, ExecPlacement, ExecPosition


class CompsocUserInline(admin.StackedInline):
    model = CompsocUser


class ShellAccountInline(admin.StackedInline):
    model = ShellAccount


class DatabaseAccountInline(admin.StackedInline):
    model = DatabaseAccount


class CompsocUserAdmin(BaseUserAdmin):
    inlines = [
        CompsocUserInline,
        ShellAccountInline,
        DatabaseAccountInline
    ]

admin.site.unregister(get_user_model())
admin.site.register(get_user_model(), CompsocUserAdmin)
admin.site.register(ExecPosition)
admin.site.register(ExecPlacement)