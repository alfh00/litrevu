# from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm


class CrispyAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(CrispyAuthenticationForm, self).__init__(*args, **kwargs)

        # Change the label for the 'username' field to 'email'
        self.fields["username"].label = "Email"


class SignupForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ("email",)
