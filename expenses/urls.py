from django.urls import path

from .views import *

app_name = "expenses"

urlpatterns = [
    path("", dashboard, name="dashboard"),

    path(
        "transactions/",
        transaction_list,
        name="transaction_list",
    ),

    path(
        "transactions/add/",
        transaction_create,
        name="transaction_create",
    ),

    path(
        "budgets/add/",
        budget_create,
        name="budget_create",
    ),
]