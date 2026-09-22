from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import *
from django.contrib.auth import get_user_model

User = get_user_model()

INPUT_CLASSES = (
    "block w-full rounded-lg border border-slate-300 bg-white px-3 py-2.5 "
    "text-sm text-slate-900 shadow-sm outline-none transition "
    "placeholder:text-slate-400 focus:border-indigo-500 "
    "focus:ring-2 focus:ring-indigo-500/20"
)

class EditProfileForm(forms.ModelForm):

    class Meta:
        model = User

        fields = [
            "first_name",
            "last_name",
            "email",
        ]

        widgets = {
            "first_name": forms.TextInput(
                attrs={
                    "class": INPUT_CLASSES,
                    "placeholder": "First name",
                }
            ),

            "last_name": forms.TextInput(
                attrs={
                    "class": INPUT_CLASSES,
                    "placeholder": "Last name",
                }
            ),

            "email": forms.EmailInput(
                attrs={
                    "class": INPUT_CLASSES,
                    "placeholder": "Email address",
                }
            ),
        }

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