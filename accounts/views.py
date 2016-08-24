from django.views.generic import View, RedirectView
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin


class MemberProfileView(LoginRequiredMixin, View):
    login_url = '/accounts/login/'
    redirect_field_name = 'redirect_to'
    template_name = 'accounts/profile.html'

    def get(self, request):
        return render(request, self.template_name)


class MemberRootRedirectView(RedirectView):
    permanent = True

    def get_redirect_url(self, *args, **kwargs):
        if self.request.user.is_authenticated():
            return '/accounts/profile'
        else:
            return '/accounts/login'
