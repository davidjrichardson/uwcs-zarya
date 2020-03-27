from django.conf.urls import url

from . import views

urlpatterns = [
    # url('^events/$', views.EventListView.as_view(), name='events_list_view'),
    # url('^events/signup/$', views.EventSignupView.as_view(), name='events_signup_view'),
    # url('^events/deregister/(?P<event_id>[0-9]+)/$', views.EventDeregisterView.as_view(), name='events_deregister_view'),
    url('^me$', views.LanAppProfileView.as_view(), name='lanapp_profile_view'),
    url('^me/music$', views.MusicAppProfileView.as_view(), name='musicapp_profile_view'),
    url('^user/(?P<uni_id>[0-9]+)/$', views.MemberDiscordInfoApiView.as_view(), name='discord_user_view'),
]
