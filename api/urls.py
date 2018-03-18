from django.conf.urls import url, include

from . import views

urlpatterns = [
    url('^discord/(?P<uni_id>[0-9]+)/$', views.MemberDiscordInfoApiView.as_view(), name='discord_user_view'),
]
