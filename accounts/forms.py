from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import *


class RegisterForm(UserCreationForm):

    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password1",
            "password2",
        ]

    def clean_email(self):
        email = self.cleaned_data["email"]

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "An account with this email already exists."
            )

        return email

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
                "display_name",
                "school_email",
                "major",
                "year",
                "graduation_year",
                "bio",
                "discord_username",
                "linkedin_url",
                "public_profile",
            ]