from django.core.urlresolvers import reverse
from django.forms.utils import ErrorList
from django.forms.forms import NON_FIELD_ERRORS
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView
from django.views.generic.base import View
from django.views.generic.edit import FormView

from authemail import wrapper

from .forms import SignupForm, LoginForm, PasswordResetForm
from .forms import PasswordResetVerifiedForm, PasswordChangeForm


class LandingView(TemplateView):
    template_name = 'landing.html'


class SignupView(FormView):
    template_name = 'signup.html'
    form_class = SignupForm

    def form_valid(self, form):
        first_name = form.cleaned_data['first_name']
        last_name = form.cleaned_data['last_name']
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']

        account = wrapper.Authemail()
        response = account.signup(first_name=first_name, last_name=last_name,
            email=email, password=password)

        # Handle other error responses from API
        if 'detail' in response:
            form.add_error(None, response['detail'])
            return self.form_invalid(form)

        return super(SignupView, self).form_valid(form)

    def get_success_url(self):
        return reverse('signup_email_sent_page')


class SignupEmailSentView(TemplateView):
    template_name = 'signup_email_sent.html'


class SignupVerifyView(View):
    def get(self, request, format=None):
        code = request.GET.get('code', '')

        account = wrapper.Authemail()
        response = account.signup_verify(code=code)

        # Handle other error responses from API
        if 'detail' in response:
            return HttpResponseRedirect(reverse('signup_not_verified_page'))

        return HttpResponseRedirect(reverse('signup_verified_page'))


class SignupVerifiedView(TemplateView):
    template_name = 'signup_verified.html'


class SignupNotVerifiedView(TemplateView):
    template_name = 'signup_not_verified.html'


class LoginView(FormView):
    template_name = 'login.html'
    form_class = LoginForm

    def form_valid(self, form):
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']

        account = wrapper.Authemail()
        response = account.login(email=email, password=password)

        if 'token' in response:
            self.request.session['auth_token'] = response['token']
        else:
            # Handle other error responses from API
            if 'detail' in response:
                form.add_error(None, response['detail'])
            return self.form_invalid(form)

        return super(LoginView, self).form_valid(form)

    def get_success_url(self):
        return reverse('home_page')


class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)

        token = self.request.session['auth_token']

        account = wrapper.Authemail()
        response = account.users_me(token=token)

        context['email'] = response['email']

        return context


class LogoutView(View):
    def get(self, request):
        token = self.request.session['auth_token']

        account = wrapper.Authemail()
        response = account.logout(token=token)

        self.request.session.flush()

        return HttpResponseRedirect(reverse('landing_page'))


class PasswordResetView(FormView):
    template_name = 'password_reset.html'
    form_class = PasswordResetForm

    def form_valid(self, form):
        email = form.cleaned_data['email']

        account = wrapper.Authemail()
        response = account.password_reset(email=email)

        # Handle other error responses from API
        if 'detail' in response:
            form.add_error(None, response['detail'])
            return self.form_invalid(form)

        return super(PasswordResetView, self).form_valid(form)

    def get_success_url(self):
        return reverse('password_reset_email_sent_page')


class PasswordResetEmailSentView(TemplateView):
    template_name = 'password_reset_email_sent.html'


class PasswordResetVerifyView(View):
    def get(self, request, format=None):
        code = request.GET.get('code', '')

        account = wrapper.Authemail()
        response = account.password_reset_verify(code=code)

        # Handle other error responses from API
        if 'detail' in response:
            return HttpResponseRedirect(
                reverse('password_reset_not_verified_page'))

        request.session['password_reset_code'] = code

        return HttpResponseRedirect(reverse('password_reset_verified_page'))


class PasswordResetVerifiedView(FormView):
    template_name = 'password_reset_verified.html'
    form_class = PasswordResetVerifiedForm

    def form_valid(self, form):
        code = self.request.session['password_reset_code']
        password = form.cleaned_data['password']

        account = wrapper.Authemail()
        response = account.password_reset_verified(code=code, password=password)

        # Handle other error responses from API
        if 'detail' in response:
            form.add_error(None, response['detail'])
            return self.form_invalid(form)

        return super(PasswordResetVerifiedView, self).form_valid(form)

    def get_success_url(self):
        return reverse('password_reset_success')


class PasswordResetNotVerifiedView(TemplateView):
    template_name = 'password_reset_not_verified.html'


class PasswordResetSuccessView(TemplateView):
    template_name = 'password_reset_success.html'


class PasswordChangeView(FormView):
    template_name = 'password_change.html'
    form_class = PasswordChangeForm

    def form_valid(self, form):
        token = self.request.session['auth_token']
        password = form.cleaned_data['password']

        account = wrapper.Authemail()
        response = account.password_change(token=token, password=password)

        # Handle other error responses from API
        if 'detail' in response:
            form.add_error(None, response['detail'])
            return self.form_invalid(form)

        return super(PasswordChangeView, self).form_valid(form)

    def get_success_url(self):
        return reverse('home_page')
