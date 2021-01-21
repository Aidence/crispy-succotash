from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView

from crispy.apps.web.forms.register import CrispyUserRegistration


class RegisterView(FormView):
    form_class = CrispyUserRegistration
    template_name = 'generic/form.html'
    success_url = '/'

    def form_valid(self, form: UserCreationForm):
        form.save()
        user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password1'])
        login(self.request, user)
        messages.success(self.request, "Great success! Enjoy :)")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['headline'] = 'Sign Up'
        context['title'] = 'User Registration'
        context['hide_header'] = True
        return context


class HomeView(TemplateView):
    template_name = "pages/home.html"

    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect(reverse('feed_list'))
        else:
            return super().get(request, *args, **kwargs)
