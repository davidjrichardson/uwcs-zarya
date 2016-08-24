from django.views.generic import View
from django.shortcuts import render


class MemberProfileView(View):
    template_name = 'accounts/profile.html'

    def get(self, request):
        return render(request, self.template_name)