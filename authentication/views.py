from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.views.generic import View
from django.conf import settings


from django.contrib.auth.forms import AuthenticationForm

from . import forms

# Create your views here.

class LoginPageView(View):
    template_name = 'authentication/login.html'
    form_class = AuthenticationForm

    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        form = self.form_class()
        message = ''
        return render(request, self.template_name, context={'form': form, 'message': message})
        
    def post(self, request):
        form = self.form_class(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
        message = 'Identifiants invalides.'
        return render(request, self.template_name, context={'form': form, 'message': message})

class SignupPageView(View):
    template_name = 'authentication/register.html'
    form_calss = forms.SignupForm

    def get(self, request):
        form = self.form_calss()
        message = ''
        return render(request, self.template_name, context={'form': form, 'message': message})    

    def post(self, request):
        form = self.form_calss(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(settings.LOGIN_REDIRECT_URL)
        message = ''
        return render(request, self.template_name, context={'form': form, 'message': message}) 


def logout_user(request):
    logout(request)
    return redirect('login')