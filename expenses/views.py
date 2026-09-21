from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def dashboard(request):
    return render(
        request,
        "expenses/dashboard.html",
    )


@login_required
def transaction_list(request):
    return render(
        request,
        "coming_soon.html",
    )


@login_required
def transaction_create(request):
    return render(
        request,
        "coming_soon.html",
    )


@login_required
def budget_create(request):
    return render(
        request,
        "coming_soon.html",
    )