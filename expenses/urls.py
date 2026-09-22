from django.urls import path

from .views import *


app_name = "expenses"


urlpatterns = [
    path(
        "",
        dashboard,
        name="dashboard",
    ),

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
        "transactions/<int:pk>/edit/",
        transaction_update,
        name="transaction_update",
    ),

    path(
        "transactions/<int:pk>/delete/",
        transaction_delete,
        name="transaction_delete",
    ),

    path(
        "budgets/add/",
        budget_create,
        name="budget_create",
    ),

    path(
        "budgets/",
        budget_list,
        name="budget_list",
    ),

    path(
        "budgets/add/",
        budget_create,
        name="budget_create",
    ),

    path(
        "budgets/<int:pk>/edit/",
        budget_update,
        name="budget_update",
    ),

    path(
        "budgets/<int:pk>/delete/",
        budget_delete,
        name="budget_delete",
    ),

    path("reports/", reports, name="reports"),

path(
    "categories/",
    category_list,
    name="category_list",
),

path(
    "categories/add/",
    category_create,
    name="category_create",
),

path(
    "categories/<int:pk>/edit/",
    category_update,
    name="category_update",
),

path(
    "categories/<int:pk>/delete/",
    category_delete,
    name="category_delete",
),

]