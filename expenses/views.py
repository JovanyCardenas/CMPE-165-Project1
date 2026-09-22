from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from datetime import date

from .forms import *
from .models import *
from .utils import ensure_default_categories


@login_required
def dashboard(request):
    ensure_default_categories(request.user)

    today = timezone.localdate()

    # ---------------------------------------------------------
    # All transactions belonging to the logged-in user
    # ---------------------------------------------------------
    transactions = (
        Transaction.objects
        .filter(user=request.user)
        .select_related("category")
    )

    # ---------------------------------------------------------
    # Current month transactions
    # ---------------------------------------------------------
    monthly_transactions = transactions.filter(
        date__year=today.year,
        date__month=today.month,
    )

    monthly_income = (
        monthly_transactions
        .filter(transaction_type=Transaction.INCOME)
        .aggregate(total=Sum("amount"))["total"]
        or Decimal("0.00")
    )

    monthly_expenses = (
        monthly_transactions
        .filter(transaction_type=Transaction.EXPENSE)
        .aggregate(total=Sum("amount"))["total"]
        or Decimal("0.00")
    )

    # Overall balance uses all transactions
    total_income = (
        transactions
        .filter(transaction_type=Transaction.INCOME)
        .aggregate(total=Sum("amount"))["total"]
        or Decimal("0.00")
    )

    total_expenses_all_time = (
        transactions
        .filter(transaction_type=Transaction.EXPENSE)
        .aggregate(total=Sum("amount"))["total"]
        or Decimal("0.00")
    )

    balance = total_income - total_expenses_all_time

    # ---------------------------------------------------------
    # Current month budgets
    # ---------------------------------------------------------
    budgets = (
        Budget.objects
        .filter(
            user=request.user,
            month__year=today.year,
            month__month=today.month,
        )
        .select_related("category")
    )

    total_budget = (
        budgets.aggregate(total=Sum("amount"))["total"]
        or Decimal("0.00")
    )

    budget_remaining = total_budget - monthly_expenses

    if budget_remaining < 0:
        budget_remaining = Decimal("0.00")

    if total_budget > 0:
        budget_percentage = (
            monthly_expenses / total_budget
        ) * 100
    else:
        budget_percentage = Decimal("0")

    # Prevent progress bar from becoming wider than its container
    budget_percentage_display = min(
        budget_percentage,
        Decimal("100"),
    )

    # ---------------------------------------------------------
    # Spending by category
    # ---------------------------------------------------------
    category_totals = (
        monthly_transactions
        .filter(
            transaction_type=Transaction.EXPENSE,
            category__isnull=False,
        )
        .values(
            "category__name"
        )
        .annotate(
            total=Sum("amount")
        )
        .order_by("-total")
    )

    category_spending = []

    for item in category_totals:

        if monthly_expenses > 0:
            percentage = (
                item["total"] / monthly_expenses
            ) * 100
        else:
            percentage = Decimal("0")

        category_spending.append(
            {
                "category": item["category__name"],
                "total": item["total"],
                "percentage": round(percentage, 1),
            }
        )

    # ---------------------------------------------------------
    # Recent transactions
    # ---------------------------------------------------------
    recent_transactions = transactions[:5]

    context = {
        "balance": balance,

        # Dashboard cards represent this month
        "total_income": monthly_income,
        "total_expenses": monthly_expenses,

        "total_budget": total_budget,
        "budget_remaining": budget_remaining,

        "budget_percentage": budget_percentage,
        "budget_percentage_display": budget_percentage_display,

        "category_spending": category_spending,

        "recent_transactions": recent_transactions,

        "current_month": today,
    }

    return render(
        request,
        "expenses/dashboard.html",
        context,
    )


@login_required
def transaction_list(request):
    ensure_default_categories(request.user)

    transactions = (
        Transaction.objects
        .filter(user=request.user)
        .select_related("category")
    )

    # Get filter values from URL
    search = request.GET.get("search", "").strip()
    transaction_type = request.GET.get("type", "").strip()
    category_id = request.GET.get("category", "").strip()
    month = request.GET.get("month", "").strip()

    # Search description and notes
    if search:
        transactions = transactions.filter(
            Q(description__icontains=search)
            | Q(notes__icontains=search)
        )

    # Income / Expense
    if transaction_type in [
        Transaction.INCOME,
        Transaction.EXPENSE,
    ]:
        transactions = transactions.filter(
            transaction_type=transaction_type
        )

    # Category
    if category_id:
        transactions = transactions.filter(
            category_id=category_id,
            category__user=request.user,
        )

    # Month: YYYY-MM
    if month:
        try:
            year, month_number = map(
                int,
                month.split("-")
            )

            transactions = transactions.filter(
                date__year=year,
                date__month=month_number,
            )

        except (ValueError, TypeError):
            pass

    categories = (
        Category.objects
        .filter(user=request.user)
        .order_by("name")
    )

    today = timezone.localdate()

    month_choices = []

    for offset in range(-12, 13):
        year = today.year
        month_number = today.month + offset

        while month_number > 12:
            month_number -= 12
            year += 1

        while month_number < 1:
            month_number += 12
            year -= 1

        month_date = date(year, month_number, 1)

        month_choices.append({
            "value": month_date.strftime("%Y-%m"),
            "label": month_date.strftime("%B %Y"),
        })

    # Totals for the currently filtered results
    filtered_income = (
        transactions
        .filter(transaction_type=Transaction.INCOME)
        .aggregate(total=Sum("amount"))["total"]
        or Decimal("0.00")
    )

    filtered_expenses = (
        transactions
        .filter(transaction_type=Transaction.EXPENSE)
        .aggregate(total=Sum("amount"))["total"]
        or Decimal("0.00")
    )

    context = {
        "transactions": transactions,
        "categories": categories,

        "search": search,
        "selected_type": transaction_type,
        "selected_category": category_id,
        "selected_month": month,

        "month_choices": month_choices,

        "filtered_income": filtered_income,
        "filtered_expenses": filtered_expenses,
    }

    return render(
        request,
        "expenses/transaction_list.html",
        context,
    )


@login_required
def transaction_create(request):
    ensure_default_categories(request.user)

    if request.method == "POST":
        form = TransactionForm(
            request.POST,
            user=request.user,
        )

        if form.is_valid():
            transaction = form.save(commit=False)

            transaction.user = request.user

            transaction.save()

            messages.success(
                request,
                "Transaction added successfully.",
            )

            return redirect(
                "expenses:transaction_list"
            )

    else:
        form = TransactionForm(
            user=request.user,
        )

    return render(
        request,
        "expenses/transaction_form.html",
        {
            "form": form,
            "page_title": "Add Transaction",
            "button_text": "Add Transaction",
        },
    )


@login_required
def transaction_update(request, pk):
    transaction = get_object_or_404(
        Transaction,
        pk=pk,
        user=request.user,
    )

    if request.method == "POST":
        form = TransactionForm(
            request.POST,
            instance=transaction,
            user=request.user,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Transaction updated successfully.",
            )

            return redirect(
                "expenses:transaction_list"
            )

    else:
        form = TransactionForm(
            instance=transaction,
            user=request.user,
        )

    return render(
        request,
        "expenses/transaction_form.html",
        {
            "form": form,
            "page_title": "Edit Transaction",
            "button_text": "Save Changes",
        },
    )


@login_required
def transaction_delete(request, pk):
    transaction = get_object_or_404(
        Transaction,
        pk=pk,
        user=request.user,
    )

    if request.method == "POST":
        transaction.delete()

        messages.success(
            request,
            "Transaction deleted successfully.",
        )

        return redirect(
            "expenses:transaction_list"
        )

    return render(
        request,
        "expenses/transaction_confirm_delete.html",
        {
            "transaction": transaction,
        },
    )

@login_required
def budget_list(request):
    ensure_default_categories(request.user)

    budgets = (
        Budget.objects
        .filter(user=request.user)
        .select_related("category")
    )

    budget_data = []

    for budget in budgets:

        spent = (
            Transaction.objects
            .filter(
                user=request.user,
                transaction_type=Transaction.EXPENSE,
                category=budget.category,
                date__year=budget.month.year,
                date__month=budget.month.month,
            )
            .aggregate(total=Sum("amount"))["total"]
            or Decimal("0.00")
        )

        remaining = budget.amount - spent

        if budget.amount > 0:
            percentage = (
                spent / budget.amount
            ) * 100
        else:
            percentage = Decimal("0")

        budget_data.append(
            {
                "budget": budget,
                "spent": spent,
                "remaining": remaining,
                "percentage": percentage,
                "percentage_display": min(
                    percentage,
                    Decimal("100"),
                ),
            }
        )

    return render(
        request,
        "expenses/budget_list.html",
        {
            "budget_data": budget_data,
        },
    )


@login_required
def budget_create(request):
    ensure_default_categories(request.user)

    if request.method == "POST":
        form = BudgetForm(
            request.POST,
            user=request.user,
        )

        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = request.user
            budget.save()

            messages.success(
                request,
                "Budget created successfully.",
            )

            return redirect("expenses:budget_list")

    else:
        form = BudgetForm(
            user=request.user,
        )

    return render(
        request,
        "expenses/budget_form.html",
        {
            "form": form,
            "page_title": "Create Budget",
            "button_text": "Create Budget",
        },
    )


@login_required
def budget_update(request, pk):
    budget = get_object_or_404(
        Budget,
        pk=pk,
        user=request.user,
    )

    if request.method == "POST":
        form = BudgetForm(
            request.POST,
            instance=budget,
            user=request.user,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Budget updated successfully.",
            )

            return redirect("expenses:budget_list")

    else:
        form = BudgetForm(
            instance=budget,
            user=request.user,
        )

    return render(
        request,
        "expenses/budget_form.html",
        {
            "form": form,
            "page_title": "Edit Budget",
            "button_text": "Save Changes",
        },
    )


@login_required
def budget_delete(request, pk):
    budget = get_object_or_404(
        Budget,
        pk=pk,
        user=request.user,
    )

    if request.method == "POST":
        budget.delete()

        messages.success(
            request,
            "Budget deleted successfully.",
        )

        return redirect("expenses:budget_list")

    return render(
        request,
        "expenses/budget_confirm_delete.html",
        {
            "budget": budget,
        },
    )