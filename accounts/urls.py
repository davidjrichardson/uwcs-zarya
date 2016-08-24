from django.conf.urls import url, include
from django.contrib.auth.views import login, logout

from . import views

urlpatterns = [
    url('^profile/', views.MemberProfileView.as_view(), name='profile_view'),
    url('^logout/', logout, name='logout_view'),
    url('^login/', login, name='login_view'),
    url('^', include('django.contrib.auth.urls')),
]
