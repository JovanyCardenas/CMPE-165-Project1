from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.contrib import messages

from .forms import *


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("profile")
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})


@login_required
def profile(request):
    return render(request, "accounts/profile.html")

@login_required
def edit_profile(request):

    if request.method == "POST":

        form = EditProfileForm(
            request.POST,
            instance=request.user,
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Your profile has been updated successfully.",
            )

            return redirect("profile")

    else:

        form = EditProfileForm(
            instance=request.user,
        )

    return render(
        request,
        "accounts/edit_profile.html",
        {
            "form": form,
        },
    )