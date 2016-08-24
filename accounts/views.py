from django.views.generic import View
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin


class MemberProfileView(LoginRequiredMixin, View):
    login_url = '/accounts/login/'
    redirect_field_name = 'redirect_to'
    template_name = 'accounts/profile.html'

    def get(self, request):
        return render(request, self.template_name)
