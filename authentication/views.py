from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import View

from . import forms

# Create your views here.


class LoginPageView(View):
    template_name = "authentication/login.html"
    form_class = forms.CrispyAuthenticationForm

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("home")
        form = self.form_class()
        message = ""
        return render(request, self.template_name, context={"form": form, "message": message})

    def post(self, request):
        form = self.form_class(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Re-bienvenue! Nous sommes ravis de vous revoi")
            return redirect("home")
        message = ""
        messages.error(request, "Identifiants invalides.", extra_tags="danger")
        # Adding a success message with the Bootstrap alert-success class
        return render(request, self.template_name, context={"form": form, "message": message})


class SignupPageView(View):
    template_name = "authentication/register.html"
    form_calss = forms.SignupForm

    def get(self, request):
        form = self.form_calss()
        message = ""
        return render(request, self.template_name, context={"form": form, "message": message})

    def post(self, request):
        form = self.form_calss(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Félicitation, création de compte réussie")
            return redirect(settings.LOGIN_REDIRECT_URL)
        message = ""
        return render(request, self.template_name, context={"form": form, "message": message})


def logout_user(request):
    logout(request)
    messages.success(request, "A bientôt")
    return redirect("login")
