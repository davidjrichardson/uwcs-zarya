from django.views.generic import View, RedirectView
from django.views.generic.edit import FormView
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model

from .models import CompsocUser
from .forms import CompsocUserForm, ShellAccountForm, DatabaseAccountForm


class MemberAccountView(LoginRequiredMixin, View):
    login_url = '/accounts/login/'
    redirect_field_name = 'redirect_to'
    template_name = 'accounts/account.html'

    def get(self, request):
        return render(request, self.template_name)


class MemberAccountUpdateView(LoginRequiredMixin, FormView):
    login_url = '/accounts/login/'
    redirect_field_name = 'redirect_to'
    template_name = 'accounts/account_update.html'
    success_url = 'done/'
    form_class = CompsocUserForm

    def get_initial(self):
        try:
            info = self.request.user.compsocuser
            return {
                'nickname': info.nickname,
                'website_url': info.website_url,
                'website_title': info.website_title,
            }
        except CompsocUser.DoesNotExist:
            return None

    def form_valid(self, form):
        account = form.save(commit=False)
        account.user = self.request.user
        if CompsocUser.objects.filter(user=self.request.user).first():
            CompsocUser.objects.filter(user=self.request.user).update(nickname=account.nickname,
                                                                      website_url=account.website_url,
                                                                      website_title=account.website_title)
        else:
            print("Saving new object")
            account.save()

        return super(MemberAccountUpdateView, self).form_valid(form)


class MemberProfileView(View):
    template_name = 'accounts/profile.html'

    def get(self, request, uid):
        user = get_object_or_404(get_user_model(), id=uid)

        return render(request, self.template_name, {'user': user})


class RequestShellAccountView(LoginRequiredMixin, FormView):
    login_url = '/accounts/login/'
    redirect_field_name = 'redirect_to'
    template_name = 'accounts/request_shell.html'
    success_url = 'done/'
    form_class = ShellAccountForm

    def form_valid(self, form):
        account = form.save(commit=False)
        account.user = self.request.user
        account.status = 'RE' # Requested
        account.save()

        return super(RequestShellAccountView, self).form_valid(form)


class RequestDatabaseAccountView(LoginRequiredMixin, FormView):
    login_url = '/accounts/login/'
    redirect_field_name = 'redirect_to'
    template_name = 'accounts/request_database.html'
    success_url = 'done/'
    form_class = DatabaseAccountForm

    def form_valid(self, form):
        account = form.save(commit=False)
        account.user = self.request.user
        account.status = 'RE' # Requested
        account.save()

        return super(RequestDatabaseAccountView, self).form_valid(form)


class RootRedirectView(RedirectView):
    permanent = True

    def get_redirect_url(self, *args, **kwargs):
        if self.request.user.is_authenticated():
            return '/accounts/profile'
        else:
            return '/accounts/login'


class RequestAccountDoneView(LoginRequiredMixin, View):
    login_url = '/accounts/login/'
    redirect_field_name = 'redirect_to'
    template_name = 'accounts/request_account_done.html'

    def get(self, request):
        return render(request, self.template_name)


class MemberAccountUpdateDoneView(LoginRequiredMixin, View):
    login_url = '/accounts/login/'
    redirect_field_name = 'redirect_to'
    template_name = 'accounts/account_update_done.html'

    def get(self, request):
        return render(request, self.template_name)