from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

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

    def nickname(self, obj):
        return CompsocUser.objects.get(user=obj).nickname


CompsocUserAdmin.list_display = ('username', 'nickname', 'email', 'first_name', 'last_name', 'is_staff')
CompsocUserAdmin.search_fields = ('username', 'compsocuser__nickname', 'first_name', 'last_name', 'email')

admin.site.unregister(get_user_model())
admin.site.register(get_user_model(), CompsocUserAdmin)
admin.site.register(ExecPosition)
admin.site.register(ExecPlacement)
