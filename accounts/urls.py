from django.conf.urls import url, include

from . import views

urlpatterns = [
    url('^profile/', views.MemberProfileView.as_view(), name='profile'),
    url('^$', views.MemberRootRedirectView.as_view(), name='root_redirect_view'),
    url('^', include('django.contrib.auth.urls')),
]
