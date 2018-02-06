from django.conf.urls import url, include

from . import views

urlpatterns = [
    url('^', include('django.contrib.auth.urls')),
    url('^$', views.RootRedirectView.as_view(), name='root_redirect_view'),
    url('^api/(?P<uni_id>[0-9]+)/$', views.MemberDiscordInfoApiView.as_view(), name='discord_user_view'),
    url('^profile/$', views.MemberAccountView.as_view(), name='profile'),
    url('^nightmode/$', views.ToggleNightModeView.as_view(), name='toggle_night_mode'),
    url('^profile/update/$', views.MemberAccountUpdateView.as_view(), name='profile_update'),
    url('^profile/update/done/$', views.MemberAccountUpdateDoneView.as_view(), name='profile_update_done'),
    url('^profile/(?P<uid>[0-9]+)/$', views.MemberProfileView.as_view(), name='public_profile'),
    url('^profile/request_shell/$', views.RequestShellAccountView.as_view(), name='request_shell'),
    url('^profile/request_database/$', views.RequestDatabaseAccountView.as_view(), name='request_database'),
    url('^profile/request_shell/done/$', views.RequestAccountDoneView.as_view(), name='request_shell_done'),
    url('^profile/request_database/done/$', views.RequestAccountDoneView.as_view(),name='request_database_done'),
]
