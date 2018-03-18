from django.conf.urls import url, include

from . import views

urlpatterns = [
    # url('^events/$') # TODO: Create events list
    # url('^events/signup/(?P<event_id>[0-9]+)/$') # TODO: Create events signup endpoint
    url('^user/(?P<uni_id>[0-9]+)/$', views.MemberDiscordInfoApiView.as_view(), name='discord_user_view'),
]
